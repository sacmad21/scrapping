import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from detailed_scraper import *



# === GET URL & PROXY FROM COMMAND LINE ===
hospital_url = sys.argv[1]  # URL from command line
proxy_address = sys.argv[2]  # Proxy from command line

# === SETUP CHROME OPTIONS WITH PROXY ===
chrome_options = Options()
chrome_options.add_argument(f'--proxy-server={proxy_address}')
chrome_options.add_argument("--headless")  # Run in background
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# === LAUNCH CHROME WEBDRIVER ===
service = Service("/path/to/chromedriver")  # Update path
driver = webdriver.Chrome(service=service, options=chrome_options)










try:
    driver.get(hospital_url)
    print(f"✅ Successfully scraped: {hospital_url}")
except Exception as e:
    print(f"⚠️ Scraper failed for {hospital_url}: {str(e)}")
finally:
    driver.quit()
