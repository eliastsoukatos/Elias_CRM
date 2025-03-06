
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

# Import the scraper
from clutch_scraper import run_clutch_scraper

# Run the scraper with the specified parameters
run_clutch_scraper(
    startUrls=['https://clutch.co/us/developers/artificial-intelligence?agency_size=250+-+999'],
    maxItems=3,
    excludePortfolio=True,
    includeReviews=False,
    maxReviewsPerCompany=0,
    batch_tag="steven",
    batch_id="663b6cc2-0845-4a15-8f79-463162b66fd2"
)

# Show completion message
print("\nScraper completed successfully!")
print("Batch ID: 663b6cc2-0845-4a15-8f79-463162b66fd2")
input("Press Enter to continue...")
                        