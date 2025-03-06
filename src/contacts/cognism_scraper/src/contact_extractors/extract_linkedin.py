from selenium.webdriver.common.by import By

def extract_linkedin(driver):
    """Extracts the LinkedIn profile URL from the webpage."""
    try:
        # Find the LinkedIn anchor tag
        linkedin_element = driver.find_element(By.XPATH, "//a[contains(@href, 'linkedin.com/in/')]")
        linkedin_url = linkedin_element.get_attribute("href").strip()

        # Debugging print statement (remove in production)
        print(f"🔗 Extracted LinkedIn URL: {linkedin_url}")

        return linkedin_url
    except Exception as e:
        print(f"⚠️ Error extracting LinkedIn URL: {e}")
        return "Not found"
