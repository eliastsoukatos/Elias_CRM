import time
import os
from utils_contacts.database import save_to_db, print_db_path
from utils_contacts.scraper import scrape_page
from utils.selenium_setup import initialize_driver
from utils_contacts.read_db import get_urls_from_db
from utils_contacts.no_duplicates import filter_new_urls
from utils.auth import wait_for_manual_login
from utils_contacts.navigate import open_new_tabs
from config import SCRAPING_DELAY  # ✅ Import randomized delay time

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Oculta los warnings de TensorFlow


def run_contacts_scraper():
    """Main process for Cognism scraping."""

    # Initialize WebDriver
    driver = initialize_driver()

    # Open Cognism login page
    driver.get("https://app.cognism.com/auth/sign-in")
    wait_for_manual_login(driver)

    # Save the initial login tab
    login_tab = driver.current_window_handle

    # Load only new URLs that are not in the database
    url_entries = filter_new_urls()

    if not url_entries:
        print("⚠️ No new URLs found. All entries already exist in the database.")
        return

    # ✅ Extract only unique URLs for processing
    urls = [entry["url"] for entry in url_entries]

    print(f"✅ {len(urls)} new URLs found and ready for processing.")

    # Process URLs in batches
    for batch_index, tabs in enumerate(open_new_tabs(driver, urls)):
        for tab_index, tab in enumerate(tabs):
            try:
                driver.switch_to.window(tab)  # Switch to opened tab

                # Get data entry (segment, timestamp, URL)
                data_entry = url_entries[(batch_index * len(tabs)) + tab_index]

                extracted_data = scrape_page(driver)  # Extract data

                if extracted_data:
                    # ✅ Merge extracted data with metadata (segment, timestamp, URL)
                    extracted_data.update({
                        "Segment": data_entry["segment"],
                        "Timestamp": data_entry["timestamp"],
                        "Cognism URL": data_entry["url"]
                    })

                    # Add contact_id if it exists in data_entry
                    if "contact_id" in data_entry:
                        extracted_data["contact_id"] = data_entry["contact_id"]

                    # ✅ Rename keys to match the database column names
                    corrected_data = {
                        "Name": extracted_data.get("Name"),
                        # ✅ Fix mismatched key
                        "Last_Name": extracted_data.get("Last Name"),
                        # ✅ Fix mismatched key
                        "Mobile_Phone": extracted_data.get("Mobile Phone"),
                        "Email": extracted_data.get("Email"),
                        "Role": extracted_data.get("Role"),
                        "City": extracted_data.get("City"),
                        "State": extracted_data.get("State"),
                        "Country": extracted_data.get("Country"),
                        "Timezone": extracted_data.get("Timezone"),
                        # ✅ Fix mismatched key
                        "LinkedIn_URL": extracted_data.get("LinkedIn URL"),
                        "Website": extracted_data.get("Website"),
                        "Timestamp": extracted_data.get("Timestamp"),
                        "Cognism_URL": extracted_data.get("Cognism URL")
                    }

                    # Only add contact_id if it exists
                    if "contact_id" in extracted_data:
                        corrected_data["contact_id"] = extracted_data.get(
                            "contact_id")

                    # ✅ Debugging print to verify corrected data
                    print("📊 Corrected Data Before Saving:", corrected_data)

                    # ✅ Ensure all required fields exist before saving
                    missing_keys = [
                        key for key, value in corrected_data.items() if value is None]

                    if missing_keys:
                        print(
                            f"⚠️ Missing keys after correction: {missing_keys}")
                    else:
                        print(f"✅ All keys are present. Proceeding to save...")
                        # ✅ Now saving corrected data
                        save_to_db(corrected_data)

                else:
                    print(f"⚠️ No data extracted for URL: {data_entry['url']}")

                time.sleep(SCRAPING_DELAY)  # ✅ Uses randomized wait time

            except Exception as e:
                print(f"⚠️ Error processing tab: {e}")

        # Close processed tabs
        for tab in tabs:
            try:
                driver.switch_to.window(tab)
                driver.close()
            except Exception as e:
                print(f"⚠️ Error closing tab: {e}")

        # Ensure switching back to login tab
        try:
            driver.switch_to.window(login_tab)
        except Exception as e:
            print(f"⚠️ Error switching back to login tab: {e}")

    print("✅ Scraping completed.")
    driver.quit()
