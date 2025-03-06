
import sys
import os

# Set up path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_companies_dir = os.path.join(current_dir, 'src_companies')
if src_companies_dir not in sys.path:
    sys.path.insert(0, src_companies_dir)

# Set up project root path for database access
project_root = os.path.dirname(os.path.dirname(current_dir))
os.environ['PROJECT_ROOT'] = project_root

# Run the scraper selector UI
from src_companies.select_scraper_ui import run_scraper_selector
run_scraper_selector()