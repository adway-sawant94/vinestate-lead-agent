# VinEstate Pitch Engine & Package Recommender
from typing import Dict, Optional

def analyze_gap_and_pitch(category: str, business_name: str, city: str, midc_zone: str = '', website: str = '', rating: float = 4.5, reviews: int = 10, decision_maker: str = 'Managing Director / Owner') -> Dict[str, str]:
    cat_lower = category.lower()
    dm_name = decision_maker.split()[0] if decision_maker and decision_maker != 'Managing Director / Owner' else 'Sir/Madam'
    zone_str = midc_zone or f"{city} Cluster"
    
    if any(k in cat_lower for k in ['villa', 'homestay', 'resort', 'stay', 'bungalow', 'cottage']):
        rec_pkg = 'Villa Revenue System (₹64,999 + AI WhatsApp Concierge)'
        gap = 'Heavy 18-22% commission loss to Airbnb/MakeMyTrip; missing direct 24/7 WhatsApp AI booking engine for weekend inquiries.'
        hook = f'Hi {dm_name}, {business_name} has great guest reviews in {city}, but relying on Airbnb/OTAs costs you 20% in margins. VinEstate builds direct booking websites and 24/7 WhatsApp AI booking concierges for luxury villas in {city} so you keep 100% of your revenue.'
    elif any(k in cat_lower for k in ['winery', 'vineyard', 'wine', 'agro-tourism']):
        rec_pkg = 'Winery Growth & Tasting Engine (₹64,999)'
        gap = 'Manual weekend wine tasting reservation handling; missing direct lead funnels for Mumbai & Pune corporate retreat groups.'
        hook = f'Hi {dm_name}, {business_name} is one of {city}\'s premier wine destinations. We help vineyards automate weekend tasting bookings via WhatsApp and run targeted B2B campaigns to attract high-paying corporate offsites from Mumbai and Pune.'
    else: # MSME / Manufacturing / Industrial
        rec_pkg = 'MSME Tech & CRM Growth Suite (₹79,999 - ₹1,45,000)'
        gap = f'Lacks automated B2B RFQ quotation engine and local/global industrial SEO for {zone_str} OEM procurement buyers.'
        hook = f'Hi {dm_name}, with manufacturing expanding across {zone_str}, procurement heads in Pune and Mumbai search for verified vendors online. VinEstate builds enterprise-grade websites, AI quotation drafting, and CRM lead pipelines tailored specifically for MSMEs in {city}.'
        
    return {
        'recommended_package': rec_pkg,
        'pain_point_gap': gap,
        'cold_pitch_hook': hook,
        'cold_pitch': hook
    }

def generate_tailored_pitch(category: str, business_name: str, city: str, growth_gap: str = '', has_website: bool = False, decision_maker: str = 'Managing Director / Owner') -> Dict[str, str]:
    res = analyze_gap_and_pitch(
        category=category,
        business_name=business_name,
        city=city,
        midc_zone=city,
        website='https://example.com' if has_website else '',
        decision_maker=decision_maker
    )
    if growth_gap:
        res['pain_point_gap'] = growth_gap
    return res
