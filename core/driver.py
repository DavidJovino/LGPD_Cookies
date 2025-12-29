from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def init_driver(headless: bool = True, timeout: int = 30):
    """Inicializa o driver do Selenium"""
    options = Options()
    if headless:
        #Caso problema tentar trocar por "--headless" apenas
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(timeout)
    return driver
        
def close_driver(driver):
    """
    Encerra o driver de forma segura.
    """
    try:
        if driver:
            driver.quit()
    except Exception:
        pass
