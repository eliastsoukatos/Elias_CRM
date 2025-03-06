from selenium.webdriver.common.by import By

def extract_email(driver):
    """Extracts email from the webpage."""
    try:
        email_element = driver.find_element(By.XPATH, "//a[contains(@class, 't-text-primary-600') and starts-with(@href, 'mailto:')]")
        return email_element.get_attribute("href").replace("mailto:", "").strip()
    except:
        return "Not found"
