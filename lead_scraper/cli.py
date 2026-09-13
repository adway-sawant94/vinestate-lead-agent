# Lead Scraper CLI Interface
import argparse
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from lead_scraper.scraper_agent import LeadScraperAgent

def main():
    parser = argparse.ArgumentParser(description='VinEstate Production Lead Scraper Command Interface')
    parser.add_argument('--category', choices=['villa', 'winery', 'msme', 'all'], default='all', help='Category')
    parser.add_argument('--city', type=str, default='all', help='City or region')
    parser.add_argument('--midc', type=str, default='all', help='MIDC zone')
    parser.add_argument('--pipeline', action='store_true', help='Run full extraction pipeline')
    
    args = parser.parse_args()
    agent = LeadScraperAgent(output_dir='Leads')
    
    if args.pipeline:
        print('Executing full extraction pipeline for VinEstate...')
        res = agent.run_complete_extraction_pipeline()
        print('\nSuccessfully generated all categorized CSV and JSON files in the "Leads/" directory.')
        return


    leads = agent.search_and_scrape(category=args.category, city=args.city, midc_zone=args.midc)
    print(f'\nFound {len(leads)} verified leads matching [Category={args.category}, City={args.city}, MIDC={args.midc}]:\n')
    print('-' * 80)
    for i, lead in enumerate(leads, 1):
        print(f'{i}. [{lead["category"] if "category" in lead else lead["Category"]}  {lead["Business Name"]}')
        print(f'    Location: {lead["Address"]} (PIN: {lead["PIN Code"]}, MIDC: {lead["MIDC Zone / Sub-Area"]})')
        print(f'    Contact:  {lead["Phone"]} | Email: {lead["Email"]}')
        print(f'    Decision Maker: {lead["Decision Maker"]} | Website: {lead["Website"]}')
        print(f'    Recommended Package: {lead["Recommended VinEstate Package"]}')
        print(f'    Pitch Hook: {lead["Tailored Pitch Hook"]}')
        print('-' * 80)

if __name__ == '__main__':
    main()
