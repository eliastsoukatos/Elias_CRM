import uuid
import re
from clutch_scraper import run_clutch_scraper
from db_initializer import check_for_database

def input_data_for_clutch_scraper():
    # Solicita número de compañías
    while True:
        num = input("Number of companies to extract: ")
        if num.isdigit() and int(num) > 0:
            num_companies = int(num)
            break
        print("Invalid input. Please enter a positive integer.")
    
    # Solicita extracción del portafolio
    while True:
        extract = input("Extract portfolio? (yes/no): ").strip().lower()
        if extract in ["yes", "no"]:
            extract_portfolio = (extract == "yes")
            break
        print("Invalid input.")
    
    # Solicita extracción de reviews
    while True:
        reviews = input("Extract reviews? (yes/no): ").strip().lower()
        if reviews in ["yes", "no"]:
            extract_reviews = (reviews == "yes")
            break
        print("Invalid input.")
    num_reviews = 0
    if extract_reviews:
        while True:
            num_r = input("Number of reviews to extract: ")
            if num_r.isdigit() and int(num_r) >= 0:
                num_reviews = int(num_r)
                break
            print("Invalid input.")
    
    # Solicita URLs
    urls = []
    print("Enter URLs one by one (type 'done' when finished):")
    while True:
        url = input("Enter URL: ").strip()
        if url.lower() == "done":
            break
        if url.startswith("http://") or url.startswith("https://"):
            urls.append(url)
        else:
            print("Invalid URL format.")
    
    # Solicita batch tag
    pattern = re.compile(r'^[A-Za-z0-9 _-]+$')
    while True:
        batch_tag = input("Enter batch tag: ").strip()
        if batch_tag and pattern.match(batch_tag):
            break
        print("Invalid batch tag.")
    
    # Genera batch ID
    batch_id = str(uuid.uuid4())
    print(f"Batch ID: {batch_id}")
    
    return {
        "num_companies": num_companies,
        "extract_portfolio": extract_portfolio,
        "extract_reviews": extract_reviews,
        "num_reviews": num_reviews,
        "urls": urls,
        "batch_tag": batch_tag,
        "batch_id": batch_id
    }

def select_scraper():
    scrapers = {"1": {"name": "Clutch Scraper", "function": input_data_for_clutch_scraper}}
    print("Select a scraper:")
    for key, val in scrapers.items():
        print(f"{key}. {val['name']}")
    choice = input("Enter your choice: ").strip()
    if choice not in scrapers:
        print("Invalid selection.")
        return

    params = scrapers[choice]["function"]()
    
    if not check_for_database():
        print("Database not found.")
        return

    print("\nSettings:")
    print(f"Companies: {params['num_companies']}")
    print(f"Portfolio: {params['extract_portfolio']}")
    print(f"Reviews: {params['extract_reviews']}")
    if params['extract_reviews']:
        print(f"Number of reviews: {params['num_reviews']}")
    print(f"URLs: {params['urls']}")
    print(f"Batch tag: {params['batch_tag']}")
    print(f"Batch ID: {params['batch_id']}")
    
    confirm = input("Proceed? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Scraper run cancelled.")
        return

    try:
        run_clutch_scraper(
            startUrls=params['urls'],
            maxItems=params['num_companies'],
            excludePortfolio=not params['extract_portfolio'],
            includeReviews=params['extract_reviews'],
            maxReviewsPerCompany=params['num_reviews'],
            batch_tag=params['batch_tag'],
            batch_id=params['batch_id']
        )
    except Exception as e:
        print(f"Error during scraping: {e}")

if __name__ == '__main__':
    select_scraper()
