from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

def initialize_driver():
    """Configures and initializes the Selenium WebDriver for Chrome with suppressed logs."""
    
    options = webdriver.ChromeOptions()
    
    # Opciones para reducir logs y mejorar estabilidad
    options.add_argument("--start-maximized")  # Pantalla completa
    options.add_argument("--disable-dev-shm-usage")  # Previene crashes en entornos limitados
    options.add_argument("--no-sandbox")  # Evita problemas en contenedores
    options.add_argument("--disable-gpu")  # Evita errores en algunas máquinas virtuales
    options.add_argument("--log-level=3")  # Minimiza logs de depuración
    options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])  # Reduce logs de Selenium

    # Inicializar WebDriver sin logs visibles
    service = Service(ChromeDriverManager().install(), log_path=os.devnull)  # Oculta logs
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver
