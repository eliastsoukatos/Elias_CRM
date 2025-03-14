
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_companies_dir = os.path.join(current_dir, 'src_companies')
if src_companies_dir not in sys.path:
    sys.path.insert(0, src_companies_dir)

os.environ['PROJECT_ROOT'] = os.path.dirname(os.path.dirname(current_dir))
os.environ['DB_PATH'] = r"/Users/anthonyhurtado/Jobs/personal/others/Elias_CRM/databases/database.db"

from clutch_scraper import run_clutch_scraper

run_clutch_scraper(
    startUrls=['https://clutch.co/web-developers'],
    maxItems=2,
    excludePortfolio=True,
    includeReviews=False,
    maxReviewsPerCompany=0,
    batch_tag="clutch_scrape_test",
    batch_id="22e1c606-e957-4514-9e0d-7afa0faffe68"
)

print("\nScraper completed successfully!")
print("Batch ID: 22e1c606-e957-4514-9e0d-7afa0faffe68")
input("Press Enter to continue...")
                        