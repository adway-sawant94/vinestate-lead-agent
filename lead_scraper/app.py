import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Request, Query, Body, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

from lead_scraper.db import (
    get_all_leads,
    update_lead_crm,
    get_stats,
    insert_or_ignore_lead,
    set_setting,
    get_setting,
    purge_all_demo_leads,
    clear_all_leads,
    delete_lead
)
from lead_scraper.places_api import GooglePlacesEngine

app = FastAPI(title="VinEstate Google Places Live Lead Engine & CRM")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# Initialize engine with stored key or env
stored_key = get_setting("GOOGLE_PLACES_API_KEY", os.environ.get("GOOGLE_PLACES_API_KEY", ""))
places_engine = GooglePlacesEngine(api_key=stored_key)

class CRMUpdateRequest(BaseModel):
    call_status: Optional[str] = None
    follow_up_date: Optional[str] = None
    sales_remarks: Optional[str] = None

class APIKeyRequest(BaseModel):
    api_key: str

class LiveSearchRequest(BaseModel):
    query: str
    category: str = "MSME / Manufacturing"
    city: str = "Nashik"
    state: str = "Maharashtra"
    limit: int = 20

class BatchExtractRequest(BaseModel):
    category: str
    state: str = "Maharashtra"
    city_or_midc: str = "Nashik"
    count: int = 50

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    html_path = BASE_DIR / "templates" / "index.html"
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/leads")
async def get_leads_api(
    category: str = "all",
    state: str = "all",
    city: str = "all",
    midc: str = "all",
    status: str = "all",
    search: str = "",
    no_website_only: bool = False
):
    leads = get_all_leads(
        category=category,
        state=state,
        city=city,
        midc=midc,
        status=status,
        search=search,
        no_website_only=no_website_only
    )
    return {"success": True, "count": len(leads), "leads": leads}

@app.get("/api/stats")
async def get_stats_api():
    stats = get_stats()
    api_key_configured = bool(places_engine.get_api_key())
    return {"success": True, "stats": stats, "api_key_configured": api_key_configured}

@app.get("/api/settings/api-key")
async def get_api_key_status():
    key = places_engine.get_api_key()
    if not key:
        return {"configured": False, "masked_key": ""}
    masked = key[:4] + "..." + key[-4:] if len(key) > 8 else "***"
    return {"configured": True, "masked_key": masked}

@app.post("/api/settings/api-key")
async def save_api_key(payload: APIKeyRequest):
    new_key = payload.api_key.strip()
    if not new_key:
        raise HTTPException(status_code=400, detail="API key cannot be empty.")
    set_setting("GOOGLE_PLACES_API_KEY", new_key)
    places_engine.set_api_key(new_key)
    return {"success": True, "message": "Google Places API Key successfully saved and activated!"}

@app.post("/api/places/search-live")
async def live_places_search(payload: LiveSearchRequest):
    if not places_engine.get_api_key():
        raise HTTPException(
            status_code=400, 
            detail="Google Places API Key is not set. Please enter your API Key in Settings."
        )

    try:
        leads = places_engine.fetch_live_leads(
            query=payload.query,
            category=payload.category,
            city=payload.city,
            state=payload.state,
            limit=payload.limit
        )
        new_inserted = 0
        for lead in leads:
            if insert_or_ignore_lead(lead):
                new_inserted += 1

        stats = get_stats()
        return {
            "success": True,
            "message": f"Successfully extracted {len(leads)} live Google businesses ({new_inserted} new leads added).",
            "total_found": len(leads),
            "new_leads_added": new_inserted,
            "leads": leads,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/places/extract-batch")
async def extract_batch_target(payload: BatchExtractRequest):
    if not places_engine.get_api_key():
        raise HTTPException(
            status_code=400, 
            detail="Google Places API Key is required. Please set your key in the dashboard header."
        )

    targets = []
    cat = payload.category
    loc = payload.city_or_midc
    st = payload.state

    if cat == "Luxury Villas & Stays" or cat == "All":
        targets.extend([
            {"cat": "Luxury Villas & Stays", "q": f"luxury villas in {loc} {st}", "city": loc},
            {"cat": "Luxury Villas & Stays", "q": f"private pool villa resort {loc} {st}", "city": loc},
            {"cat": "Luxury Villas & Stays", "q": f"homestay luxury cottages {loc} {st}", "city": loc},
        ])

    if cat == "Wineries & Vineyards" or cat == "All":
        targets.extend([
            {"cat": "Wineries & Vineyards", "q": f"wineries vineyard {loc} {st}", "city": loc},
            {"cat": "Wineries & Vineyards", "q": f"wine tasting estate resort {loc} {st}", "city": loc},
        ])

    if cat == "MSME / Manufacturing" or cat == "All":
        targets.extend([
            {"cat": "MSME / Manufacturing", "q": f"manufacturing industries {loc} {st}", "city": loc},
            {"cat": "MSME / Manufacturing", "q": f"engineering works industrial {loc} {st}", "city": loc},
            {"cat": "MSME / Manufacturing", "q": f"fabrication precision components {loc} {st}", "city": loc},
            {"cat": "MSME / Manufacturing", "q": f"packaging plastic mouldings {loc} {st}", "city": loc},
        ])

    total_added = 0
    all_extracted = []

    try:
        for t in targets:
            if total_added >= payload.count:
                break
            leads = places_engine.fetch_live_leads(
                query=t["q"],
                category=t["cat"],
                city=t["city"],
                state=st,
                limit=20
            )
            for lead in leads:
                if total_added >= payload.count:
                    break
                if insert_or_ignore_lead(lead):
                    total_added += 1
                    all_extracted.append(lead)

        stats = get_stats()
        return {
            "success": True,
            "message": f"Batch extraction complete! Added {total_added} fresh live Google Places leads.",
            "new_leads_added": total_added,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/purge-demo")
async def purge_demo_endpoint():
    count = purge_all_demo_leads()
    stats = get_stats()
    return {"success": True, "message": f"Purged {count} non-live/demo leads.", "stats": stats}

@app.post("/api/admin/clear-all")
async def clear_all_endpoint():
    count = clear_all_leads()
    stats = get_stats()
    return {"success": True, "message": f"Cleared all {count} leads from database.", "stats": stats}

@app.delete("/api/leads/{lead_id}")
async def delete_single_lead(lead_id: int):
    success = delete_lead(lead_id)
    return {"success": success, "lead_id": lead_id}

@app.put("/api/leads/{lead_id}/crm")
async def update_crm_status(lead_id: int, payload: CRMUpdateRequest):
    success = update_lead_crm(
        lead_id=lead_id,
        call_status=payload.call_status,
        follow_up_date=payload.follow_up_date,
        sales_remarks=payload.sales_remarks
    )
    return {"success": success, "lead_id": lead_id}

@app.get("/api/download/csv")
async def download_csv_export(
    category: str = "all",
    state: str = "all",
    city: str = "all",
    status: str = "all"
):
    leads = get_all_leads(category=category, state=state, city=city, status=status)
    if not leads:
        return JSONResponse(status_code=400, content={"error": "No leads found for specified filters."})

    export_df = pd.DataFrame(leads)
    
    col_map = {
        "business_name": "Business Name",
        "category": "Category",
        "state": "State",
        "city": "City",
        "industrial_zone": "MIDC / Zone",
        "pin_code": "PIN Code",
        "address": "Full Formatted Address",
        "phone": "Direct Calling Phone",
        "whatsapp_link": "WhatsApp Direct Chat Link",
        "website": "Live Website URL",
        "google_rating": "Google Star Rating",
        "reviews_count": "Total Google Reviews",
        "google_maps_url": "Google Maps Verification Link",
        "call_status": "CRM Call Status",
        "follow_up_date": "Next Follow-up Date",
        "sales_remarks": "Sales Call Remarks",
        "growth_gap": "Identified Growth Gap",
        "recommended_package": "Recommended VinEstate Package",
        "tailored_pitch_hook": "Tailored Cold Call / WhatsApp Pitch Hook"
    }
    
    export_cols = [c for c in col_map.keys() if c in export_df.columns]
    export_df = export_df[export_cols].rename(columns=col_map)
    
    export_path = os.path.join(BASE_DIR.parent, "Leads", f"google_places_leads_{category}_{city}.csv")
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    export_df.to_csv(export_path, index=False, encoding="utf-8-sig")
    
    return FileResponse(export_path, filename=os.path.basename(export_path), media_type="text/csv")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8050)
