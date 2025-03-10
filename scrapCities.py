import time
import pandas as pd
import util as util
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)




def scrape_cities():
    df_states = pd.read_csv("stateList.csv")
    city_data = []
    
    driver = get_driver()
    wait = WebDriverWait(driver, 30)

    for _, row in df_states.iterrows():
        state_name = row["State"]
        state_url = row["State URL"]

        util.log_message(f"Scraping cities for: {state_name} | URL: {state_url}")
        driver.get(state_url)
        time.sleep(5)

        try:
            directory_map_wrap = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@class='directory_map_wrap'][h2[contains(text(), 'Search Hospital by Cities & Towns')]]")
            ))

            city_links = directory_map_wrap.find_elements(By.XPATH, ".//ul[@class='directory_map_list']/li/a")

            for city_link in city_links:
                city_name = city_link.text.strip()
                city_url = city_link.get_attribute("href")
                city_data.append({"State": state_name, "City": city_name, "City URL": city_url})
        
        except Exception as e:
            util.log_message(f"❌ ERROR: No cities found for {state_name}. {str(e)}", "error")
            continue

    driver.quit()

    df_cities = pd.DataFrame(city_data)
    df_cities.to_csv("cityList.csv", index=False)
    util.log_message("🎉 City scraping completed. Data saved to cityList.csv!")

if __name__ == "__main__":
    scrape_cities()
