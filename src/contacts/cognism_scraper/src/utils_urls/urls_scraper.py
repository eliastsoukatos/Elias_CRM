from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime

def scrape_urls(driver, segment):
    """Extrae todos los URLs de perfiles de personas en la página implementando desplazamiento para listas virtualizadas."""
    try:
        # Espera a que la página cargue completamente
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Esperar la presencia de la tabla con la lista de personas
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@href, '/search/prospects/persons/') and contains(@class, 't-text-primary-600')]"))
        )
        
        # Encontrar el contenedor de desplazamiento virtual
        scroll_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "cdk-virtual-scroll-viewport"))
        )
        
        # Lista para guardar los URLs únicos
        seen_urls = set()
        previous_count = 0

        while True:
            # Buscar todos los enlaces en la tabla
            url_elements = driver.find_elements(By.XPATH, "//a[contains(@href, '/search/prospects/persons/') and contains(@class, 't-text-primary-600')]")
            
            for elem in url_elements:
                href = elem.get_attribute("href")
                if href and "/search/prospects/persons/" in href:
                    full_url = f"https://app.cognism.com{href}" if href.startswith("/") else href
                    seen_urls.add(full_url)

            # Desplazar hacia abajo en el contenedor virtual
            driver.execute_script("arguments[0].scrollBy(0, 300);", scroll_container)
            time.sleep(1.5)  # Esperar a que se carguen los nuevos elementos

            # Si no se agregan más URLs, detener el bucle
            if len(seen_urls) == previous_count:
                break

            previous_count = len(seen_urls)

        # Crear lista de diccionarios con URLs, segmento y timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        urls_data = [{"url": url, "segment": segment, "timestamp": timestamp} for url in seen_urls]
        
        print(f"✅ Total URLs Extracted: {len(seen_urls)}")
        print(urls_data)
        return {"URLs": urls_data}

    except Exception as e:
        print(f"⚠️ Error during scrolling & scraping: {e}")
        return None
