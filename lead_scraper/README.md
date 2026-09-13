# VinEstate Production Lead Scraper & Growth Engine

A production-grade, multi-source lead scraper agent engineered for **VinEstate (Agency)** to achieve the **₹4,00,000 revenue target in 4 months**.

## Target Verticals & Regions
1. **Luxury Villas & Homestays**: Nashik (Gangapur Dam, Anjaneri, Trimbakeshwar), Igatpuri (Manas Road, Bhavali Dam, Hill Station), Lonavala, Alibaug.
2. **Wineries & Vineyards**: Nashik Wine Belt, Gangapur, Dindori, Niphad, Sanjegaon, Vinchur Wine Park.
3. **MSME Industrial Manufacturing**: Ambad MIDC, Satpur MIDC, Sinnar & Musalgaon MIDC, Igatpuri Gonde MIDC, Pune (Chakan & Bhosari MIDC), Sambhajinagar (Waluj MIDC).

---

## The 0% City Mismatch Solution
Standard lead scrapers suffer from 90% city confusion (misclassifying Nashik/Sinnar/Igatpuri businesses as Pune or Mumbai). This engine fixes that using:
- **Strict Reverse Geocoding & Postal PIN Validation** (4220xx for Nashik, 422103 for Sinnar/Musalgaon MIDC, 422403 for Igatpuri/Gonde MIDC).
- **MIDC Cluster Geofencing** for all Maharashtra industrial zones.
- **Physical Property vs Headquarter Disambiguation**.

---

## Quick Start & Usage

### 1. Run Complete Extraction Pipeline (Generates all CSV/JSON leads)
`ash
python -m lead_scraper.cli --pipeline
`

### 2. Search & Scrape by Category, City, or MIDC Zone via CLI
`ash
# Filter Luxury Villas in Igatpuri
python -m lead_scraper.cli --category villa --city igatpuri

# Filter MSMEs in Ambad MIDC
python -m lead_scraper.cli --category msme --midc ambad

# Filter Wineries in Nashik
python -m lead_scraper.cli --category winery --city nashik
`

### 3. Launch Interactive Web Dashboard
`ash
python lead_scraper/app.py
`
Open **http://127.0.0.1:8050** in your browser to:
- Live filter by Category, Region, and MIDC
- 1-click WhatsApp pitch messaging
- Direct phone call buttons
- Instant CSV / JSON lead exports

---

## Generated Lead Files (Leads/ directory)
- Leads/villas_nashik_igatpuri_verified.csv / .json
- Leads/wineries_maharashtra_verified.csv / .json
- Leads/msme_nashik_sinnar_midc_verified.csv / .json
- Leads/msme_maharashtra_wide_verified.csv / .json
- Leads/master_verified_leads_vinestate.csv / .json
