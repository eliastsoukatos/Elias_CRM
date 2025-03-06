from selenium.webdriver.common.by import By

def extract_role(driver):
    """Extracts the person's job title (role) from the webpage."""
    try:
        # Find the first div inside the role/location container
        role_element = driver.find_element(By.XPATH, "//div[contains(@class, 't-text-sm t-text-dark-400')]/div[1]")

        role = role_element.text.strip()
        
        # Debugging print statement (remove in production)
        print(f"💼 Extracted Role: {role}")

        return role
    except Exception as e:
        print(f"⚠️ Error extracting role: {e}")
        return "Not found"
