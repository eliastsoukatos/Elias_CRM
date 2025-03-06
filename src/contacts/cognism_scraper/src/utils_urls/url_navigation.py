from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from utils_urls.urls_scraper import scrape_urls
from utils_urls.input_urls_db import save_urls_to_db

def navigate_and_scrape(driver, segment):
    """Navigates through pages and scrapes contacts until the last page."""
    page_number = 1  # Track the number of pages scraped

    while True:
        print(f"📄 Scraping Page {page_number}...")

        # Scrape the current page
        urls_data = scrape_urls(driver, segment)
        if urls_data and "URLs" in urls_data:
            save_urls_to_db(urls_data["URLs"])

        # Check pagination text to determine if we're on the last page
        try:
            pagination_text = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.t-text-xs.t-mr-2"))
            ).text
        except:
            print("⚠️ Could not find pagination info. Assuming last page.")
            break  # If we can't find the pagination, assume it's the last page

        # Extract the numbers from the pagination text
        numbers = [int(num) for num in pagination_text.split() if num.isdigit()]

        if len(numbers) >= 3:
            current_last = numbers[1]  # Second number in pagination (e.g., 144)
            total_count = numbers[2]   # Third number in pagination (e.g., 144)
            
            if current_last == total_count:
                print("✅ Reached the last page. Stopping scraping.")
                break

        # Try to find the 'Next' button
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-cognism='paginate-next-a']"))
            )
        except:
            print("✅ Next button not found. Assuming last page.")
            break  # If the button doesn't exist, stop scraping

        # Click the next button
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(3)  # Wait for new data to load

        page_number += 1  # Move to the next page
