import json
import time
import util as util
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Load Config
with open("data_config.json", "r") as file:
    config = json.load(file)

# Initialize WebDriver
def get_driver():
    options = Options()
    # options.add_argument("--headless")  # Disable headless for debugging
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Scrape Hospital Listings from States & Cities
def scrape_listing():
    driver = get_driver()
    driver.get("https://www.medindia.net/directories/hospitals/index.htm")

    util.log_message("Opened MedIndia hospital directory.")
    time.sleep(5)  # Ensure full page load

    wait = WebDriverWait(driver, 30)  # Increased wait time

    try:
        # ✅ Corrected XPath for State Links
        state_links = wait.until(EC.visibility_of_all_elements_located(
            (By.XPATH, "//ul[@class='directory_map_list']/li[@class='directory_map_list_item']/a")
        ))
    except Exception as e:
        util.log_message(f"❌ ERROR: State links not found! {str(e)}", "error")
        driver.quit()
        return

    if not state_links:
        util.log_message("❌ ERROR: No state links found!", "error")
        driver.quit()
        return

    hospitals = []
    existing_data = util.load_progress("hospital_list_progress.csv")
    visited_states = set([d["State"] for d in existing_data]) if existing_data else set()



    for state_link in state_links:
        state_name = state_link.text.strip()
        if state_name in visited_states:
            util.log_message(f"Skipping already scraped state: {state_name}")
            continue

        state_url = state_link.get_attribute("href")
        util.log_message(f"Scraping state: {state_name} | URL: {state_url}")
        driver.get(state_url)
        time.sleep(5)  # Ensure state page loads

        try:
            # Find the correct directory_map_wrap <div> that contains the required <h2>
            directory_map_wrap = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@class='directory_map_wrap'][h2[contains(text(), 'Search Hospital by Cities & Towns')]]")
            ))

            # Extract city links from its <ul>
            city_links = directory_map_wrap.find_elements(By.XPATH, ".//ul[@class='directory_map_list']/li/a")
            
            
            totalCities = len(city_links)
            util.log_message(f"Found CitiesScraping : {totalCities}")
            
        except Exception as e:
            util.log_message(f"❌ ERROR: No cities found for {state_name}. {str(e)}", "error")
            continue
            

        for city_link in city_links:            
            city_url = city_link.get_attribute("href")
            print("City URL:" , city_url)

            city_name = city_link.text.strip()
            city_url = city_link.get_attribute("href")
            util.log_message(f"Scraping city: {city_name} | URL: {city_url}")
            driver.get(city_url)
            time.sleep(5)  # Ensure city page loads

            # Extract hospital listings
            page_num = 1
            while True:
                try:
                    # ✅ Corrected XPath for Hospital Listings
                    hospital_list = wait.until(EC.visibility_of_all_elements_located(
                        (By.XPATH, "//div[@class='strip_box']")
                    ))
                except Exception as e:
                    util.log_message(f"❌ ERROR: No hospitals found on page {page_num} in {city_name}. {str(e)}", "error")
                    break  # Stop pagination if no hospitals are found

                util.log_message(f"Scraping hospitals in {city_name} (Page {page_num})...")

                for hospital in hospital_list:
                    hospital_data = {}
                    try:
                        hospital_name = hospital.find_element(By.XPATH, ".//h3/a").text.strip()
                        hospital_url = hospital.find_element(By.XPATH, ".//h3/a").get_attribute("href")
                        hospital_address = hospital.find_element(By.XPATH, ".//p").text.strip()
                    except:
                        hospital_name, hospital_url, hospital_address = "N/A", "N/A", "N/A"

                    hospital_data["Name"] = hospital_name
                    hospital_data["URL"] = hospital_url
                    hospital_data["Address"] = hospital_address
                    hospital_data["State"] = state_name
                    hospital_data["City"] = city_name
                    hospitals.append(hospital_data)
                    util.save_to_csv(hospitals, "hospital_list_progress.csv")
                    util.random_wait(1, 10)  # Random wait to avoid bot detection

                # Check for pagination
                try:
                    next_page = driver.find_element(By.LINK_TEXT, str(page_num + 1))
                    next_page.click()
                    util.log_message(f"Navigating to Page {page_num + 1}...")
                    time.sleep(5)
                    page_num += 1
                except:
                    util.log_message(f"End of pages for {city_name}.", "info")
                    break  # No more pages

    driver.quit()
    util.save_to_csv(hospitals, "hospital_list.csv")
    util.log_message("🎉 Listing page scraping completed!")

    # Keep browser open for debugging
    input("Press Enter to exit...")

if __name__ == "__main__":
    scrape_listing()
