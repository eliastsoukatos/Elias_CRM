import os
from utils.auth import wait_for_manual_login
from utils.selenium_setup import initialize_driver
from utils_urls.url_navigation import navigate_and_scrape

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Hides TensorFlow warnings

def run_urls_scraper():
    """Logs into Cognism using Selenium, waits for manual login, and scrapes all available contacts."""
    
    # Initialize WebDriver
    driver = initialize_driver()

    # Open Cognism login page
    driver.get("https://app.cognism.com/auth/sign-in")
    wait_for_manual_login(driver)

    print("✅ Successfully logged into Cognism.")
    print("Now create a search of contacts on Cognism and input their segment.")

    # Prompt user for input
    segment = input("📌 Input the Company's Industry Segment: ")

    print(f"✅ Industry segment selected: {segment}")

    # Start full scraping process with navigation
    navigate_and_scrape(driver, segment)

    return driver  # Optional: Return driver for later use
