import sys
import requests
from selenium import webdriver

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
from detailed_scraper import * 
import traceback
import time 
import undetected_chromedriver as uc


os.chdir(os.path.dirname("/home/devzone/MyCenter/genAIProj/llamaWork/scrap_sites/"))


# === GET URL & PROXY FROM ARGUMENTS ===
name = sys.argv[1]  # URL from command line
url = sys.argv[2]  # URL from command line
proxy_address = sys.argv[3]  # Proxy from command line


def getBrightDataProxyDriver():

    # curl -i --proxy brd.superproxy.io:33335 --proxy-user brd-customer-hl_b803b7e4-zone-indi786:j2vucdkhy6bp -k "https://geo.brdtest.com/welcome.txt?product=resi&method=native"
    # URL : brd.superproxy.io:33335 
    # --proxy-user brd-customer-hl_b803b7e4-zone-indi786:j2vucdkhy6bp 

    return ""

def getWebDriver() :
    # === CONFIGURE SELENIUM PROXY ===
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"--proxy-server={proxy_address}")
    # chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # === LAUNCH SELENIUM BROWSER ===

    #service = Service("/path/to/chromedriver")  # Update this
    chromeservice=Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=chromeservice, options=chrome_options)
    return driver


def getUndetectedDriver() :
#=== SETUP UNDETECTED CHROME DRIVER (NO HEADLESS) ===
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument(f'--proxy-server={proxy_address}')
    # chrome_options.add_argument("--headless")  # ❌ Remove this to keep browser visible

    # === LAUNCH CHROME WEBDRIVER WITH PROXY ===
    driver = uc.Chrome(options=chrome_options)


# Define the log message
log_message = f"✅ Initiating Scraper : {name}, {url}, {proxy_address}\n"
# Write to the log file
with open("/home/devzone/scrapping/proxy_scrapper_monitoring.log", "a") as log_file:
    log_file.write(log_message)

print(f"✅ Initiating Scrapper : {name}, {url} , {proxy_address}")







try:

    address,phone,email,website,specialties,services = scrap_hospital_url(driver,name,url)

    print(f"✅ Successfully scraped: {url}")
    print(f"Data : {address},{phone},{email},{website},{specialties},{services}")



except Exception as e:
    traceback.print_exc()
    print(f"⚠️ Scraper failed for {url}: {str(e)}")
    time.sleep(30)

finally:
    time.sleep(30)
    driver.quit()
