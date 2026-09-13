import sqlite3
import os
from typing import List, Dict, Optional, Any

DB_PATH = os.path.join(os.path.dirname(__file__), 'crm_leads.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if table exists and has place_id
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='leads'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        cursor.execute("PRAGMA table_info(leads)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'place_id' not in columns:
            cursor.execute("DROP TABLE leads")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_id TEXT UNIQUE,
            business_name TEXT NOT NULL,
            category TEXT,
            state TEXT DEFAULT 'Maharashtra',
            city TEXT,
            district TEXT,
            industrial_zone TEXT,
            pin_code TEXT,
            address TEXT,
            phone TEXT,
            whatsapp_link TEXT,
            email TEXT,
            website TEXT,
            decision_maker TEXT,
            google_rating TEXT,
            reviews_count INTEGER DEFAULT 0,
            google_maps_url TEXT,
            growth_gap TEXT,
            recommended_package TEXT,
            tailored_pitch_hook TEXT,
            has_website INTEGER DEFAULT 1,
            call_status TEXT DEFAULT 'New / Fresh',
            follow_up_date TEXT DEFAULT '',
            sales_remarks TEXT DEFAULT '',
            is_live_google INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

def set_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default

def purge_all_demo_leads():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads WHERE is_live_google = 0 OR place_id IS NULL OR place_id = ''")
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count

def clear_all_leads():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads")
    count = cursor.rowcount
    conn.commit()
    conn.close()
    return count

def insert_or_ignore_lead(lead: Dict[str, Any]) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        biz_name = lead.get('business_name') or lead.get('Business Name')
        if not biz_name:
            return False
        
        place_id = lead.get('place_id') or ''
        site = lead.get('website') or lead.get('Website') or ''
        has_site = 1 if site and 'instagram.com' not in site and site != '' and 'google.com/maps' not in site else 0
        
        # Check duplicate by place_id or name+city
        if place_id:
            cursor.execute("SELECT id FROM leads WHERE place_id = ?", (place_id,))
            if cursor.fetchone():
                return False
        else:
            cursor.execute("SELECT id FROM leads WHERE LOWER(business_name) = ? AND LOWER(city) = ?", 
                           (biz_name.lower().strip(), (lead.get('city') or '').lower().strip()))
            if cursor.fetchone():
                return False

        cursor.execute("""
            INSERT INTO leads (
                place_id, business_name, category, state, city, district, industrial_zone,
                pin_code, address, phone, whatsapp_link, email, website,
                decision_maker, google_rating, reviews_count, google_maps_url,
                growth_gap, recommended_package, tailored_pitch_hook, has_website,
                call_status, follow_up_date, sales_remarks, is_live_google
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            place_id,
            biz_name,
            lead.get('category') or lead.get('Category', 'MSME / Manufacturing'),
            lead.get('state') or lead.get('State', 'Maharashtra'),
            lead.get('city') or lead.get('City', ''),
            lead.get('district') or lead.get('District', ''),
            lead.get('industrial_zone') or lead.get('MIDC Zone / Sub-Area', 'Industrial Area'),
            lead.get('pin_code') or lead.get('PIN Code', ''),
            lead.get('address') or lead.get('Address', ''),
            lead.get('phone') or lead.get('Phone', ''),
            lead.get('whatsapp_link') or lead.get('WhatsApp Link', ''),
            lead.get('email') or lead.get('Email', ''),
            site,
            lead.get('decision_maker') or lead.get('Decision Maker', 'Managing Director / Owner'),
            lead.get('google_rating') or lead.get('Google Rating', 'Not Rated'),
            lead.get('reviews_count', 0),
            lead.get('google_maps_url', ''),
            lead.get('growth_gap') or lead.get('Growth Gap / Pain Point', ''),
            lead.get('recommended_package') or lead.get('Recommended VinEstate Package', 'MSME Tech & CRM Suite'),
            lead.get('tailored_pitch_hook') or lead.get('Tailored Pitch Hook', ''),
            has_site,
            lead.get('call_status', 'New / Fresh'),
            lead.get('follow_up_date', ''),
            lead.get('sales_remarks', ''),
            lead.get('is_live_google', 1)
        ))
        inserted = cursor.rowcount > 0
        conn.commit()
        return inserted
    except Exception as e:
        print(f"DB Insert Error: {e}")
        return False
    finally:
        conn.close()

def get_all_leads(
    category: str = 'all',
    state: str = 'all',
    city: str = 'all',
    midc: str = 'all',
    status: str = 'all',
    search: str = '',
    no_website_only: bool = False
) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM leads WHERE 1=1"
    params = []
    if category != 'all':
        query += " AND LOWER(category) LIKE ?"
        params.append(f"%{category.lower()}%")
    if state != 'all':
        query += " AND LOWER(state) LIKE ?"
        params.append(f"%{state.lower()}%")
    if city != 'all':
        query += " AND (LOWER(city) LIKE ? OR LOWER(address) LIKE ?)"
        params.extend([f"%{city.lower()}%", f"%{city.lower()}%"])
    if midc != 'all':
        query += " AND (LOWER(industrial_zone) LIKE ? OR LOWER(address) LIKE ?)"
        params.extend([f"%{midc.lower()}%", f"%{midc.lower()}%"])
    if status != 'all':
        query += " AND LOWER(call_status) = ?"
        params.append(status.lower())
    if no_website_only:
        query += " AND (has_website = 0 OR website LIKE '%instagram.com%' OR website = '' OR website IS NULL)"
    if search:
        query += " AND (LOWER(business_name) LIKE ? OR LOWER(address) LIKE ? OR LOWER(decision_maker) LIKE ? OR phone LIKE ? OR pin_code LIKE ?)"
        s_pat = f"%{search.lower()}%"
        params.extend([s_pat, s_pat, s_pat, s_pat, s_pat])
    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    leads = [dict(row) for row in rows]
    conn.close()
    return leads

def update_lead_crm(lead_id: int, call_status: Optional[str] = None, follow_up_date: Optional[str] = None, sales_remarks: Optional[str] = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    updates = []
    params = []
    if call_status is not None:
        updates.append("call_status = ?")
        params.append(call_status)
    if follow_up_date is not None:
        updates.append("follow_up_date = ?")
        params.append(follow_up_date)
    if sales_remarks is not None:
        updates.append("sales_remarks = ?")
        params.append(sales_remarks)
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(lead_id)
    sql = f"UPDATE leads SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(sql, params)
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success

def delete_lead(lead_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def get_stats() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM leads")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leads WHERE LOWER(category) LIKE '%villa%' OR LOWER(category) LIKE '%homestay%' OR LOWER(category) LIKE '%resort%'")
    villas = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leads WHERE LOWER(category) LIKE '%winery%' OR LOWER(category) LIKE '%vineyard%' OR LOWER(category) LIKE '%wine%'")
    wineries = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leads WHERE LOWER(category) LIKE '%msme%' OR LOWER(category) LIKE '%machin%' OR LOWER(category) LIKE '%auto%' OR LOWER(category) LIKE '%fabricat%' OR LOWER(category) LIKE '%packag%' OR LOWER(category) LIKE '%electric%' OR LOWER(category) LIKE '%manufactur%'")
    msme = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leads WHERE call_status = 'New / Fresh'")
    new_leads = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leads WHERE call_status = 'Interested'")
    interested = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leads WHERE call_status = 'Follow-up Needed'")
    follow_up = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leads WHERE call_status = 'Quotation Sent'")
    quotation = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leads WHERE call_status = 'Converted / Client Won'")
    converted = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM leads WHERE has_website = 0 OR website LIKE '%instagram.com%' OR website = '' OR website IS NULL")
    no_website = cursor.fetchone()[0]
    conn.close()
    return {
        "total": total,
        "villas": villas,
        "wineries": wineries,
        "msme": msme,
        "new_leads": new_leads,
        "interested": interested,
        "follow_up": follow_up,
        "quotation": quotation,
        "converted": converted,
        "no_website": no_website
    }

init_db()
