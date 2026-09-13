import csv
import json
import os
from typing import List, Dict

def export_leads(leads: List[Dict], base_filename: str, output_dir: str = 'Leads') -> Dict[str, str]:
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f'{base_filename}.csv')
    json_path = os.path.join(output_dir, f'{base_filename}.json')
    
    if not leads:
        return {'csv': '', 'json': '', 'count': 0}
        
    fieldnames = [
        'Business Name', 'Category', 'City', 'District', 'MIDC Zone / Sub-Area',
        'PIN Code', 'Address', 'Phone', 'WhatsApp Link', 'Email', 'Website',
        'Decision Maker', 'Google Rating', 'Growth Gap / Pain Point',
        'Recommended VinEstate Package', 'Tailored Pitch Hook', 'Source'
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for lead in leads:
            writer.writerow(lead)
            
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)
        
    return {
        'csv': csv_path,
        'json': json_path,
        'count': len(leads)
    }
