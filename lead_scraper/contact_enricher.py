# VinEstate Contact Enricher & Phone/Email Formatter
import re
from typing import Dict, List, Optional
import urllib.parse

PHONE_PATTERN = re.compile(r'(?:\+91|91|0)?[\s-]?[6-9]\d{9}')
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')

def format_indian_phone(raw_phone: str) -> str:
    if not raw_phone:
        return ''
    digits = re.sub(r'\D', '', raw_phone)
    if len(digits) == 10:
        return f'+91 {digits[:5]} {digits[5:]}'
    elif len(digits) == 12 and digits.startswith('91'):
        return f'+91 {digits[2:7]} {digits[7:]}'
    elif len(digits) == 11 and digits.startswith('0'):
        return f'+91 {digits[1:6]} {digits[6:]}'
    return raw_phone.strip()

def clean_whatsapp_link(phone: str) -> str:
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        digits = '91' + digits
    elif len(digits) == 12 and digits.startswith('91'):
        pass
    else:
        return ''
    return f'https://wa.me/{digits}'

def enrich_contact_record(data: Dict) -> Dict:
    phone = data.get('phone', '')
    cleaned_phone = format_indian_phone(phone)
    wa_link = clean_whatsapp_link(phone)
    
    email = data.get('email', '').strip()
    website = data.get('website', '').strip()
    if website and not website.startswith(('http://', 'https://')):
        website = 'https://' + website
        
    return {
        **data,
        'formatted_phone': cleaned_phone,
        'whatsapp_link': wa_link,
        'clean_website': website
    }
