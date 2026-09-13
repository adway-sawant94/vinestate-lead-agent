# VinEstate Lead Scraper Agent Master Orchestrator
import os
import json
from typing import List, Dict, Optional
from lead_scraper.geo_validator import normalize_and_validate_location
from lead_scraper.contact_enricher import format_indian_phone, clean_whatsapp_link
from lead_scraper.pitch_engine import analyze_gap_and_pitch
from lead_scraper.verified_database import get_all_verified_leads
from lead_scraper.exporter import export_leads

class LeadScraperAgent:
    def __init__(self, output_dir: str = "Leads"):
        self.output_dir = output_dir
        self.verified_database = get_all_verified_leads()

    def search_and_scrape(self, category: Optional[str] = None, city: Optional[str] = None, midc_zone: Optional[str] = None) -> List[Dict]:
        results = []
        for lead in self.verified_database:
            if category and category.lower() != 'all':
                cat_lower = category.lower()
                lead_cat_lower = lead['Category'].lower()
                if cat_lower == 'villa' and not any(k in lead_cat_lower for k in ['villa', 'homestay', 'resort', 'stay', 'bungalow', 'chalet']):
                    continue
                elif cat_lower == 'winery' and not any(k in lead_cat_lower for k in ['winery', 'vineyard', 'wine']):
                    continue
                elif cat_lower == 'msme' and not any(k in lead_cat_lower for k in ['msme', 'auto', 'precision', 'machining', 'packaging', 'fabricat', 'electrical', 'moulding', 'tooling']):
                    continue
            if city and city.lower() != 'all':
                city_search = city.lower().strip()
                lead_city = lead['City'].lower()
                lead_addr = lead['Address'].lower()
                lead_midc = lead['MIDC Zone / Sub-Area'].lower()
                if city_search not in lead_city and city_search not in lead_addr and city_search not in lead_midc:
                    continue
            if midc_zone and midc_zone.lower() != 'all':
                midc_search = midc_zone.lower().strip()
                if midc_search not in lead['MIDC Zone / Sub-Area'].lower() and midc_search not in lead['Address'].lower():
                    continue
            geo = normalize_and_validate_location(lead['Address'], raw_city=lead['City'])
            lead['City'] = geo['city']
            lead['District'] = geo['district']
            lead['PIN Code'] = geo['pin_code']
            results.append(lead)
        return results

    def run_complete_extraction_pipeline(self) -> Dict[str, Dict]:
        print("Starting VinEstate Real Lead Extraction Pipeline across Maharashtra...")
        villas = self.search_and_scrape(category='villa')
        res_villas = export_leads(villas, 'villas_nashik_igatpuri_verified', self.output_dir)
        print(f"Villas extracted: {len(villas)} leads saved to {res_villas['csv']}")
        wineries = self.search_and_scrape(category='winery')
        res_wineries = export_leads(wineries, 'wineries_maharashtra_verified', self.output_dir)
        print(f"Wineries extracted: {len(wineries)} leads saved to {res_wineries['csv']}")
        msme_nashik = self.search_and_scrape(category='msme', city='nashik') + self.search_and_scrape(category='msme', city='sinnar') + self.search_and_scrape(category='msme', city='igatpuri')
        seen_names = set()
        dedup_msme = []
        for m in msme_nashik:
            if m['Business Name'] not in seen_names:
                seen_names.add(m['Business Name'])
                dedup_msme.append(m)
        res_msme_nashik = export_leads(dedup_msme, 'msme_nashik_sinnar_midc_verified', self.output_dir)
        print(f"Nashik, Sinnar, Igatpuri MIDC MSMEs: {len(dedup_msme)} leads saved to {res_msme_nashik['csv']}")
        msme_all = self.search_and_scrape(category='msme')
        res_msme_all = export_leads(msme_all, 'msme_maharashtra_wide_verified', self.output_dir)
        print(f"All Maharashtra MSMEs: {len(msme_all)} leads saved to {res_msme_all['csv']}")
        all_leads = self.search_and_scrape(category='all')
        res_master = export_leads(all_leads, 'master_verified_leads_vinestate', self.output_dir)
        print(f"Master Database: {len(all_leads)} leads saved to {res_master['csv']}")
        return {
            'villas': res_villas,
            'wineries': res_wineries,
            'msme_nashik': res_msme_nashik,
            'msme_all': res_msme_all,
            'master': res_master
        }
