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
import time
import random


def get_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def writeToFile(hospitalCounter, state_name, city_name, hospital_name, hospital_url, hospital_address):



    fileId =  ( hospitalCounter // 1000 ) + 1 
    state_code = state_name[:4].upper() 

    fileName = f"data/hospitals/hl_{fileId}.csv"
    with open(fileName, "a") as file:
        rowData = f"{hospitalCounter},{state_name},{city_name},{hospital_name},{hospital_url},{hospital_address}\n"
        file.write(rowData)
        print(rowData)


def scrape_hospitals():
    df_cities = pd.read_csv("data/cityList.csv")
    existing_hospitals = set()
    hospitalCounter = 1
    try:
        df_existing = pd.read_csv("hospitalList.csv")
        existing_hospitals = set(df_existing["Hospital URL"])
    except FileNotFoundError:
        pass

    driver = get_driver()
    wait = WebDriverWait(driver, 30)
#   State,City,City URL,

    for cityIndex, row in df_cities.iterrows():
        state_name = row["State"]
        city_name = row["City"]
        city_url = row["City URL"]

        util.log_message(f"Scraping hospitals in: {city_name}, {state_name}")
        driver.get(city_url)
        time.sleep(5)

        page_num = 1
        while True:
            try:
                hospital_list = wait.until(EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@class='strip_box']")
                ))
            except Exception as e:
                util.log_message(f"❌ ERROR: No hospitals found in {city_name}. {str(e)}", "error")
                break

            for hospital in hospital_list:
                try:
                    hospital_name = hospital.find_element(By.XPATH, ".//h3/a").text.strip()
                    hospital_url = hospital.find_element(By.XPATH, ".//h3/a").get_attribute("href")
                    hospital_address = hospital.find_element(By.XPATH, ".//p").text.strip()
                except:
                    hospital_name, hospital_url, hospital_address = "N/A", "N/A", "N/A"

                if hospital_url in existing_hospitals:
                    continue  # Skip already scraped hospitals

                util.log_message(f"✅ Hospital added: {hospital_name} | {hospital_url}")
                hospitalCounter += 1 

                writeToFile(hospitalCounter, state_name, city_name, hospital_name, hospital_url, hospital_address)

            # Check for pagination
            try:
                next_page = driver.find_element(By.LINK_TEXT, str(page_num + 1))
                next_page.click()

                # Generate a random wait time between 100ms (0.1s) and 1000ms (1s)
                wait_time = random.uniform(10, 30)  # Converts milliseconds to seconds
                time.sleep(wait_time)  # Pause execution
                print("Resumed execution!")
                page_num += 1
            except:
                break  # No more pages

    driver.quit()
    util.log_message("🎉 Hospital scraping completed!")

if __name__ == "__main__":
    scrape_hospitals()
