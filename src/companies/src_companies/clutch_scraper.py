from apify_client import ApifyClient
from preprocessor import preprocessor


def run_clutch_scraper(startUrls, maxItems, excludePortfolio, includeReviews, maxReviewsPerCompany, batch_tag, batch_id):
    try:
        # Validación de parámetros
        if not isinstance(startUrls, list):
            raise ValueError("startUrls must be a list.")
        for url in startUrls:
            if not isinstance(url, str) or not url.startswith("http"):
                raise ValueError(f"Invalid URL: {url}")
        if not isinstance(maxItems, int) or maxItems <= 0:
            raise ValueError("maxItems must be a positive integer.")
        if not isinstance(maxReviewsPerCompany, int) or maxReviewsPerCompany < 0:
            raise ValueError("maxReviewsPerCompany must be non-negative.")
        if not isinstance(excludePortfolio, bool):
            raise ValueError("excludePortfolio must be boolean.")
        if not isinstance(includeReviews, bool):
            raise ValueError("includeReviews must be boolean.")

        client = ApifyClient("apify_api_s5EW9X8I8vaqyw4TsDveSU5nGoWiMS4rETrw")
        print("Apify client initialized.")

        run_input = {
            "customMapFunction": "(object) => { return object }",
            "excludePortfolio": excludePortfolio,
            "extendOutputFunction": "($) => { return {} }",
            "includeReviews": includeReviews,
            "maxItems": maxItems,
            "maxReviewsPerCompany": maxReviewsPerCompany,
            "mode": "profiles",
            "proxy": {"useApifyProxy": True},
            "startUrls": startUrls
        }
        print(f"Running scraper for {len(startUrls)} URL(s)...")
        run = client.actor("XBE8BJUuJZgMf2sms").call(run_input=run_input)
        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            raise ValueError("No default dataset found.")

        items = list(client.dataset(dataset_id).iterate_items())
        print(f"Found {len(items)} items in the dataset")
        for item in items:
            print(f"Processing URL: {item.get('url')}")
            preprocessor(item, batch_id, batch_tag)

        print(f"Scraper completed for batch_id: {batch_id}")
    except Exception as e:
        print(f"Error running scraper: {e}")


if __name__ == '__main__':
    run_clutch_scraper(
        startUrls=["https://clutch.co/web-developers"],
        maxItems=3,
        excludePortfolio=True,
        includeReviews=True,
        maxReviewsPerCompany=3,
        batch_tag="test",
        batch_id="dummy-id"
    )
