from selenium.webdriver.common.by import By

def extract_company(driver):
    """Extracts company details (Name, Website, Employees, Founded Year) from the webpage."""
    try:
        # Extract company name
        try:
            company_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Name:')]/parent::span")
            company_name = company_element.text.replace("Name:", "").strip()  # Remove 'Name:' prefix
        except:
            company_name = "Not found"

        # Extract website and remove 'www.'
        try:
            website_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Website:')]/following-sibling::a")
            website = website_element.get_attribute("href").replace("www.", "").strip()
        except:
            website = "Not found"

        # Extract employee headcount
        try:
            employees_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Employee Headcount')]/parent::span")
            employees = employees_element.text.replace("Employee Headcount", "").strip()
        except:
            employees = "Not found"

        # Extract founded year
        try:
            founded_element = driver.find_element(By.XPATH, "//span[contains(text(), 'Founded:')]/parent::span")
            founded_text = founded_element.text.strip()

            # Remove "Founded:" prefix
            founded = founded_text.replace("Founded:", "").strip()
        except:
            founded = "Not found"

        # Debugging print statement (remove in production)
        print(f"Company: {company_name} | Website: {website} | Employees: {employees} | Founded: {founded}")


        return company_name, website, employees, founded
    except Exception as e:
        print(f"Error extracting company details: {e}")
        return "Not found", "Not found", "Not found", "Not found"
