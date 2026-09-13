import os
import re
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Any, Optional
from lead_scraper.geo_validator import normalize_lead_location, get_pincode_zone_info
from lead_scraper.pitch_engine import generate_tailored_pitch

DEFAULT_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY") or os.environ.get("PLACES_API_KEY", "")

class GooglePlacesEngine:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or DEFAULT_PLACES_API_KEY).strip()

    def set_api_key(self, api_key: str):
        self.api_key = api_key.strip()

    def get_api_key(self) -> str:
        return self.api_key

    def search_places_new_api(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Queries Google Places API (New) - places.googleapis.com/v1/places:searchText
        """
        if not self.api_key:
            raise ValueError("Google Places API Key is missing. Please configure your API key.")

        url = "https://places.googleapis.com/v1/places:searchText"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": (
                "places.id,places.displayName,places.formattedAddress,places.nationalPhoneNumber,"
                "places.internationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,"
                "places.googleMapsUri,places.addressComponents,places.types,places.businessStatus"
            )
        }
        payload = json.dumps({"textQuery": query, "pageSize": min(limit, 20)}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("places", [])
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(error_body)
                msg = err_json.get("error", {}).get("message", error_body)
            except Exception:
                msg = error_body
            raise RuntimeError(f"Places API Error (HTTP {e.code}): {msg}")
        except Exception as e:
            raise RuntimeError(f"Network error: {str(e)}")

    def search_places_legacy_api(self, query: str) -> List[Dict[str, Any]]:
        """
        Fallback for Legacy Places API text search.
        """
        base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            "query": query,
            "key": self.api_key,
            "region": "in"
        }
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "VinEstate-Lead-Engine/2.0"})
        
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            status = data.get("status")
            if status not in ("OK", "ZERO_RESULTS"):
                raise RuntimeError(f"Legacy API Error: {data.get('error_message', status)}")
            return data.get("results", [])

    def transform_new_place_to_lead(self, place: Dict[str, Any], category: str, fallback_city: str = "", fallback_state: str = "Maharashtra", fallback_midc: str = "") -> Dict[str, Any]:
        """
        Converts Places API (New) result into standard VinEstate lead dictionary.
        """
        display_name = place.get("displayName", {})
        name = display_name.get("text", "Unknown Business").strip() if isinstance(display_name, dict) else str(display_name)
        address = place.get("formattedAddress", "")
        phone = place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber") or ""
        website = place.get("websiteUri", "")
        rating = place.get("rating", 0.0)
        reviews_count = place.get("userRatingCount", 0)
        google_maps_url = place.get("googleMapsUri", "")
        place_id = place.get("id", "")
        business_status = place.get("businessStatus", "OPERATIONAL")

        # Parse address components
        pin_code = ""
        city = fallback_city
        state = fallback_state

        components = place.get("addressComponents", [])
        for comp in components:
            types = comp.get("types", [])
            long_name = comp.get("longText") or comp.get("long_name", "")
            if "postal_code" in types:
                pin_code = long_name
            elif "locality" in types and long_name:
                city = long_name
            elif "administrative_area_level_1" in types and long_name:
                state = long_name

        if not pin_code and address:
            pin_matches = re.findall(r"\b\d{6}\b", address)
            if pin_matches:
                pin_code = pin_matches[-1]

        # Use geo validator
        geo_fixed = normalize_lead_location({
            "business_name": name,
            "address": address,
            "pin_code": pin_code,
            "city": city,
            "state": state,
            "industrial_zone": fallback_midc
        })

        clean_city = geo_fixed.get("city", city)
        clean_state = geo_fixed.get("state", state)
        clean_zone = geo_fixed.get("industrial_zone", fallback_midc or f"{clean_city} Zone")
        clean_pin = geo_fixed.get("pin_code", pin_code)

        # Phone formatting & WhatsApp
        clean_phone = phone
        clean_digits = re.sub(r"[^\d]", "", phone)
        whatsapp_link = ""
        if len(clean_digits) >= 10:
            last10 = clean_digits[-10:]
            clean_phone = f"+91 {last10[:5]} {last10[5:]}"
            whatsapp_link = f"https://wa.me/91{last10}"

        rating_str = f"{rating} ★ ({reviews_count} reviews)" if rating else "Not Rated"

        # Opportunity / gap detection
        has_real_website = bool(website and ("http" in website) and ("google.com" not in website.lower()))
        
        if category == "Luxury Villas & Stays":
            if not has_real_website:
                growth_gap = "Zero direct booking website — 100% dependent on Airbnb/MakeMyTrip losing 18-22% commission per stay."
            elif reviews_count < 30:
                growth_gap = "Low online review volume and missing automated guest re-engagement funnel."
            else:
                growth_gap = "Missing instant VIP direct WhatsApp booking automation & revenue management system."
        elif category == "Wineries & Vineyards":
            if not has_real_website:
                growth_gap = "No direct-to-consumer digital cellar door or online tasting tour booking portal."
            else:
                growth_gap = "Missing B2B HoReCa distributor portal and automated wine club membership subscriptions."
        else: # MSME & Industrial
            if not has_real_website:
                growth_gap = "No OEM-grade digital product catalogue / ISO portfolio for export & MNC client verification."
            else:
                growth_gap = "Missing automated CRM RFQ pipeline & WhatsApp quotation generation for tier-1 vendor approvals."

        pitch = generate_tailored_pitch(
            category=category,
            business_name=name,
            city=clean_city,
            growth_gap=growth_gap,
            has_website=has_real_website
        )

        return {
            "place_id": place_id,
            "business_name": name,
            "category": category,
            "state": clean_state,
            "city": clean_city,
            "industrial_zone": clean_zone,
            "pin_code": clean_pin,
            "address": address,
            "phone": clean_phone,
            "whatsapp_link": whatsapp_link,
            "email": "",
            "website": website,
            "decision_maker": "Owner / Managing Director",
            "google_rating": rating_str,
            "reviews_count": reviews_count,
            "google_maps_url": google_maps_url,
            "call_status": "New / Fresh",
            "follow_up_date": "",
            "sales_remarks": "",
            "growth_gap": growth_gap,
            "recommended_package": pitch.get("recommended_package", "VinEstate Growth Suite"),
            "tailored_pitch_hook": pitch.get("cold_pitch", ""),
            "is_verified": 1,
            "business_status": business_status
        }

    def fetch_live_leads(self, query: str, category: str, city: str, state: str = "Maharashtra", limit: int = 20) -> List[Dict[str, Any]]:
        """
        Attempts Google Places API (New) first, then legacy, or provides clean actionable error.
        """
        try:
            places = self.search_places_new_api(query, limit=limit)
            leads = []
            for p in places:
                if p.get("businessStatus") == "CLOSED_PERMANENTLY":
                    continue
                lead = self.transform_new_place_to_lead(
                    place=p,
                    category=category,
                    fallback_city=city,
                    fallback_state=state,
                    fallback_midc=f"{city} Zone"
                )
                leads.append(lead)
            return leads
        except Exception as e:
            # Check if legacy works
            try:
                legacy_places = self.search_places_legacy_api(query)
                leads = []
                for p in legacy_places[:limit]:
                    name = p.get("name", "")
                    addr = p.get("formatted_address", "")
                    pid = p.get("place_id", "")
                    rating = p.get("rating", 0.0)
                    rev = p.get("user_ratings_total", 0)
                    lead = self.transform_new_place_to_lead(
                        place={
                            "id": pid,
                            "displayName": {"text": name},
                            "formattedAddress": addr,
                            "rating": rating,
                            "userRatingCount": rev,
                            "googleMapsUri": f"https://www.google.com/maps/place/?q=place_id:{pid}"
                        },
                        category=category,
                        fallback_city=city,
                        fallback_state=state,
                        fallback_midc=f"{city} Zone"
                    )
                    leads.append(lead)
                return leads
            except Exception:
                raise e
