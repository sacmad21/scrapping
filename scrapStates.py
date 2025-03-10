import time
import util as util
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

def get_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scrape_states():
    driver = get_driver()
    driver.get("https://www.medindia.net/directories/hospitals/index.htm")

    util.log_message("Opened MedIndia hospital directory.")
    time.sleep(5)  # Ensure full page load

    wait = WebDriverWait(driver, 30)

    try:
        state_links = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//ul[@class='directory_map_list']/li[@class='directory_map_list_item']/a")
        ))
    except Exception as e:
        util.log_message(f"❌ ERROR: State links not found! {str(e)}", "error")
        driver.quit()
        return

    state_data = []
    for state_link in state_links:
        state_name = state_link.text.strip()
        state_url = state_link.get_attribute("href")
        state_data.append({"State": state_name, "State URL": state_url})

    driver.quit()

    df = pd.DataFrame(state_data)
    df.to_csv("stateList.csv", index=False)
    util.log_message("🎉 State scraping completed. Data saved to stateList.csv!")

if __name__ == "__main__":
    scrape_states()
