from selenium.webdriver.common.by import By
from data.timezones import get_timezone  # ✅ This should work now

def extract_location(driver):
    """Extracts the person's location details (City, State, Country) and assigns a timezone if available."""
    try:
        # Find the second div inside the role/location container
        location_element = driver.find_element(By.XPATH, "//div[contains(@class, 't-text-sm t-text-dark-400')]/div[2]")
        full_location = location_element.text.strip()

        # Remove unnecessary new lines
        full_location = full_location.replace("\n", ", ").replace("  ", " ")

        # Debugging print statement (remove in production)
        print(f"📍 Raw Location Extracted: {full_location}")

        # Split into City, State, Country
        location_parts = [part.strip() for part in full_location.split(",")]

        city = location_parts[0] if len(location_parts) > 0 else "Not found"
        state = location_parts[1] if len(location_parts) > 1 else "Not found"
        country = location_parts[2] if len(location_parts) > 2 else "Not found"

        # Get timezone based on state (US) or country (Europe/LatAm)
        timezone = get_timezone(state, country)

        # Debugging print statement (remove in production)
        print(f"🌍 Parsed Location: City: {city}, State: {state}, Country: {country}, Timezone: {timezone}")

        return city, state, country, timezone
    except Exception as e:
        print(f"⚠️ Error extracting location: {e}")
        return "Not found", "Not found", "Not found", "Not applicable"
