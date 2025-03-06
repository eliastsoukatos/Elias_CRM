from selenium.webdriver.common.by import By

def extract_mobile_phone(driver):
    """Extracts mobile phone number from the webpage."""
    try:
        # Look for links with "tel:" (telephone)
        phone_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'tel:')]")

        for phone_element in phone_elements:
            phone_number = phone_element.get_attribute("href").replace("tel:", "").strip()
            
            # Check if the number is labeled as "Mobile"
            try:
                parent_element = phone_element.find_element(By.XPATH, "./following-sibling::span")
                if "Mobile" in parent_element.text:
                    return phone_number
            except:
                pass

        return "Not found"

    except:
        return "Not found"
