from selenium.webdriver.common.by import By

def extract_name(driver):
    """Extracts full name from the webpage and splits it into Name and Last Name."""
    try:
        # Find the full name element
        name_element = driver.find_element(By.XPATH, "//div[contains(@class, 't-font-semibold t-text-primary-850')]")
        full_name = name_element.text.strip()

        # Split into first and last name
        name_parts = full_name.split(" ", 1)  # Splits at the first space

        first_name = name_parts[0] if name_parts else "Not found"
        last_name = name_parts[1] if len(name_parts) > 1 else "Not found"

        return first_name, last_name
    except:
        return "Not found", "Not found"
