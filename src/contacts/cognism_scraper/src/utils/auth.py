import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import COGNISM_EMAIL, COGNISM_PASSWORD

def wait_for_manual_login(driver):
    """Auto-fills login credentials and waits for login to complete automatically."""
    print("\nOpening Cognism login page...")

    # Wait for page to load and ensure login form is present
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception as e:
        print("Error: Page took too long to load.")
        return False

    # Wait until the email input field is visible
    try:
        email_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='email']"))
        )
        password_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//input[@formcontrolname='password']"))
        )

        # Clear any pre-filled values
        email_input.clear()
        password_input.clear()

        # Fill in the credentials
        email_input.send_keys(COGNISM_EMAIL)
        password_input.send_keys(COGNISM_PASSWORD)

        print("Credentials auto-filled. Please complete CAPTCHA and login manually.")
        print("The system will automatically detect when you're logged in.")
        
        # Wait for login to complete by checking for dashboard elements
        try:
            # Wait for the dashboard or some element that appears after login
            WebDriverWait(driver, 300).until(  # 5 minute timeout
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dashboard') or contains(@class, 'search-page')]"))
            )
            print("Login detected successfully!")
            return True
        except:
            # Try an alternative element - depends on the page structure
            try:
                WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, "//header[contains(@class, 'header')]"))
                )
                print("Login detected successfully!")
                return True
            except:
                print("Timeout waiting for login. Please try again.")
                return False

    except Exception as e:
        print(f"Error: Unable to locate email/password fields. \n{e}")
        return False
