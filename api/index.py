import sys
import os
from pathlib import Path

# Add project root to sys.path so modules import correctly in Vercel serverless environment
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lead_scraper.app import app

# Export handler for Vercel
# Vercel's Python runtime natively handles ASGI applications when assigned to app / handler
