# Geo Validator & City Mismatch Resolver
import re
from typing import Dict, Optional, Any

MAHARASHTRA_GEO_REGISTRY = {
    'Nashik': {
        'district': 'Nashik',
        'pin_prefixes': ['4220', '4221', '4222', '4224'],
        'known_pins': {
            '422001': 'Nashik City Central',
            '422002': 'Panchavati',
            '422003': 'Dindori Road',
            '422005': 'Gangapur Road / Govardhan',
            '422006': 'Upnagar / Nashik Road',
            '422007': 'Satpur MIDC / Trimbak Road',
            '422008': 'Indira Nagar / Pathardi',
            '422009': 'College Road / Canada Corner',
            '422010': 'Ambad MIDC / Cidco',
            '422011': 'Mhasrul',
            '422012': 'Ambad MIDC Industrial Area',
            '422013': 'Govardhan / Gangapur Dam',
            '422101': 'Nashik Road Railway Station',
            '422102': 'Deolali Camp',
            '422103': 'Sinnar MIDC / Musalgaon',
            '422104': 'Darna Dam / Bhagur',
            '422209': 'Ozar / HAL Airport',
            '422202': 'Dindori / Vani Road (Wine Belt)',
            '422222': 'Dindori Agro and Wine Cluster',
            '422401': 'Ghoti / Vaitarna',
            '422402': 'Igatpuri Town',
            '422403': 'Igatpuri Hill Station / Gonde MIDC',
            '422212': 'Trimbakeshwar / Anjaneri',
            '422303': 'Niphad / Vinchur Wine Park',
        },
        'midc_zones': [
            'Ambad MIDC', 'Satpur MIDC', 'Sinnar MIDC', 'Musalgaon MIDC',
            'Malegaon MIDC Sinnar', 'Igatpuri MIDC', 'Gonde MIDC',
            'Vinchur Wine Park', 'Dindori MIDC', 'Ozar Industrial Area'
        ]
    },
    'Sinnar': {
        'district': 'Nashik',
        'pin_prefixes': ['4221'],
        'known_pins': {
            '422103': 'Sinnar City and Musalgaon MIDC',
            '422113': 'Sinnar Rural / Malegaon MIDC'
        },
        'midc_zones': ['Sinnar MIDC', 'Musalgaon MIDC', 'Malegaon MIDC Sinnar']
    },
    'Igatpuri': {
        'district': 'Nashik',
        'pin_prefixes': ['4224'],
        'known_pins': {
            '422401': 'Ghoti / Vaitarna Backwaters',
            '422402': 'Igatpuri Town',
            '422403': 'Igatpuri Hill Station / Manas Road / Gonde MIDC'
        },
        'midc_zones': ['Gonde MIDC', 'Igatpuri MIDC']
    },
    'Pune': {
        'district': 'Pune',
        'pin_prefixes': ['4110', '4105', '4121', '4122'],
        'known_pins': {
            '410501': 'Chakan MIDC Phase 1 and 2',
            '411026': 'Bhosari Industrial Estate',
            '411018': 'Pimpri Industrial Zone',
            '410507': 'Talegaon MIDC',
            '412209': 'Ranjangaon MIDC',
            '410401': 'Lonavala / Khandala Luxury Stays'
        },
        'midc_zones': ['Chakan MIDC', 'Bhosari MIDC', 'Pimpri-Chinchwad', 'Talegaon MIDC', 'Ranjangaon MIDC']
    },
    'Chhatrapati Sambhaji Nagar': {
        'district': 'Chhatrapati Sambhaji Nagar',
        'pin_prefixes': ['4310', '4311'],
        'known_pins': {
            '431136': 'Waluj MIDC Industrial Area',
            '431007': 'Shendra MIDC / DMIC Zone',
            '431006': 'Chikalthana MIDC'
        },
        'midc_zones': ['Waluj MIDC', 'Shendra MIDC', 'Chikalthana MIDC']
    }
}

PIN_CODE_PATTERN = re.compile(r'\b([1-8]\d{5})\b')

def extract_pin_code(text: str) -> Optional[str]:
    matches = PIN_CODE_PATTERN.findall(text)
    if matches:
        return matches[-1]
    return None

def normalize_and_validate_location(raw_address: str, raw_city: str = '') -> Dict[str, str]:
    clean_addr = raw_address.strip() if raw_address else ''
    pin = extract_pin_code(clean_addr)
    addr_lower = clean_addr.lower()
    city_lower = raw_city.lower() if raw_city else ''

    detected_city = raw_city or 'Nashik'
    detected_district = raw_city or 'Nashik'
    detected_midc = 'Industrial / Commercial Zone'
    detected_sub_area = ''

    if pin:
        for reg_city, reg_data in MAHARASHTRA_GEO_REGISTRY.items():
            if pin in reg_data['known_pins']:
                detected_city = reg_city
                detected_district = reg_data['district']
                detected_sub_area = reg_data['known_pins'][pin]
                break
            else:
                for prefix in reg_data['pin_prefixes']:
                    if pin.startswith(prefix):
                        detected_city = reg_city
                        detected_district = reg_data['district']
                        break

    if any(k in addr_lower or k in city_lower for k in ['igatpuri', 'ghoti', 'bhavali', 'camel valley', 'manas resort', 'tringalwadi']):
        detected_city = 'Igatpuri'
        detected_district = 'Nashik'
        if not detected_sub_area:
            detected_sub_area = 'Igatpuri Hill Station'
    elif any(k in addr_lower or k in city_lower for k in ['sinnar', 'musalgaon', 'malegaon midc']):
        detected_city = 'Sinnar'
        detected_district = 'Nashik'
        if not detected_sub_area:
            detected_sub_area = 'Sinnar Industrial Hub'
    elif any(k in addr_lower or k in city_lower for k in ['nashik', 'nasik', 'gangapur', 'satpur', 'ambad', 'trimbak', 'anjaneri', 'panchavati', 'govardhan']):
        if detected_city not in ['Igatpuri', 'Sinnar']:
            detected_city = 'Nashik'
            detected_district = 'Nashik'

    if 'ambad' in addr_lower:
        detected_midc = 'Ambad MIDC'
    elif 'satpur' in addr_lower:
        detected_midc = 'Satpur MIDC'
    elif 'musalgaon' in addr_lower:
        detected_midc = 'Musalgaon MIDC'
    elif 'gonde' in addr_lower:
        detected_midc = 'Gonde MIDC'
    elif 'vinchur' in addr_lower:
        detected_midc = 'Vinchur Wine Park'
    elif 'chakan' in addr_lower:
        detected_midc = 'Chakan MIDC'
    elif 'bhosari' in addr_lower:
        detected_midc = 'Bhosari MIDC'
    elif 'waluj' in addr_lower:
        detected_midc = 'Waluj MIDC'

    return {
        'city': detected_city,
        'district': detected_district,
        'midc_zone': detected_midc,
        'sub_area': detected_sub_area or detected_city,
        'pin_code': pin or '',
        'full_address': clean_addr
    }

def normalize_lead_location(lead_dict: Dict[str, Any]) -> Dict[str, Any]:
    address = lead_dict.get('address', '')
    city = lead_dict.get('city', '')
    state = lead_dict.get('state', 'Maharashtra')
    pin = lead_dict.get('pin_code', '')
    zone = lead_dict.get('industrial_zone', '')

    res = normalize_and_validate_location(address, city)
    
    lead_dict['city'] = res['city'] or city or 'Nashik'
    lead_dict['state'] = state or 'Maharashtra'
    lead_dict['pin_code'] = pin or res['pin_code']
    if res['midc_zone'] != 'Industrial / Commercial Zone':
        lead_dict['industrial_zone'] = res['midc_zone']
    elif not zone:
        lead_dict['industrial_zone'] = f"{lead_dict['city']} Zone"
        
    return lead_dict

def get_pincode_zone_info(pincode: str) -> Optional[Dict[str, str]]:
    for city, data in MAHARASHTRA_GEO_REGISTRY.items():
        if pincode in data['known_pins']:
            return {'city': city, 'zone': data['known_pins'][pincode]}
    return None
