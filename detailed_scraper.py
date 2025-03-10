import os
import time
import pandas as pd
import util

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import traceback


def get_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)




def scrap_hospital_url(driver, hospital_name, hospital_url) :
    wait = WebDriverWait(driver, 30)

    util.log_message(f"Kickstart Detailed Scrapper for: {hospital_name} | {hospital_url}")
    driver.get(hospital_url)
    time.sleep(5)

    # Extract hospital details
    try:
        name = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[@class='contactName']"))).text.strip()
    except:
        name = hospital_name  # Use fallback from CSV

    try:
        address = driver.find_element(By.XPATH, "//div[@class='contactDetails']/p[b[contains(text(), 'Address')]]").text.strip()
    except:
        address = "N/A"

    # Click "View Contact Details" to open modal
    try:
        contact_button = wait.until(EC.presence_of_element_located((By.XPATH, "//a[contains(text(), 'View Contact Details')]")))

        # Scroll into view before clicking
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", contact_button)
        time.sleep(5)

        # Wait for any overlaying elements to disappear
        # WebDriverWait(driver, 5).until(EC.invisibility_of_element((By.CLASS_NAME, "disabled-link")))

        try:
            # contact_button.click()
            driver.execute_script("GetData();")
        except Exception:
            util.log_message(f"⚠️ Click intercepted! Retrying with JavaScript for {hospital_name}", "warning")
            # driver.execute_script("arguments[0].click();", contact_button)

        time.sleep(3)                  
        
        
        util.log_message(f"Contact button is clicked")
        # Wait until modal is visible
        wait.until(EC.presence_of_element_located((By.ID, "myModal")))

        # Extract contact details from modal
        try:
            phone_numbers = [elem.text.strip() for elem in driver.find_elements(By.XPATH, "//div[@id='contactDetails']//img[contains(@src, 'call.png')]/following-sibling::div/a")]
            mobile_numbers = [elem.text.strip() for elem in driver.find_elements(By.XPATH, "//div[@id='contactDetails']//img[contains(@src, 'mobile.png')]/following-sibling::div/a")]
            phone = ", ".join(phone_numbers + mobile_numbers) if (phone_numbers or mobile_numbers) else "N/A"
        except:
            phone = "N/A"

        try:
            email = driver.find_element(By.XPATH, "//div[@id='contactDetails']//img[contains(@src, 'email.png')]/following-sibling::div/a").text.strip()
        except:
            email = "N/A"

        try:
            website = driver.find_element(By.XPATH, "//div[@id='contactDetails']//img[contains(@src, 'web.png')]/following-sibling::div/a").text.strip()
        except:
            website = "N/A"

        # Close modal after extraction
        try:
            close_button = driver.find_element(By.XPATH, "//button[@class='close_button']")
            driver.execute_script("arguments[0].click();", close_button)
        except:
            util.log_message(f"⚠️ Couldn't close modal for {hospital_name}", "warning")

    except:
        traceback.print_exc()
        util.log_message(f"❌ No contact button found for {hospital_name}", "warning")
        phone, email, website = "N/A", "N/A", "N/A"

    try:
        specialties = [s.text.strip() for s in driver.find_elements(By.XPATH, "//h2[contains(text(), 'Specialties')]/following-sibling::ul/li")]
        specialties = ", ".join(specialties) if specialties else "N/A"
    except:
        traceback.print_exc()
        specialties = "N/A"

    try:
        services = [s.text.strip() for s in driver.find_elements(By.XPATH, "//h2[contains(text(), 'Services')]/following-sibling::ul/li")]
        services = ", ".join(services) if services else "N/A"
    except:
        services = "N/A"


    return address,phone,email,website,specialties,services


def scrape_hospital_details(driver = None, scapperId=None, fileId = None):

    if scapperId == None :
        scapperId = ""

    if fileId == None :
        fileId = 0 


    print("Current working directory:", os.getcwd())
    hospitalDetailFileName = f"""data/hospitals/hd{scapperId}.csv"""
    hospitalUrlList =  f"data/hospitals/hl_{fileId}.csv"
                          

    # Define column headers
    column_headers = ["State", "City", "Hospital Name", "Hospital URL", "Address", "Phone", "Email", "Website", "Specialties", "Services"]

    # Check if `hospitalDetails.csv` exists, else create it with headers
    if not os.path.exists(hospitalDetailFileName):
        pd.DataFrame(columns=column_headers).to_csv("data/hospitalDetails.csv", index=False)

    # Load `hospitalList.csv` ensuring headers are assigned correctly
    df_hospitals = pd.read_csv(hospitalUrlList, header=None, names=["Sr.No","State", "City", "Hospital Name", "Hospital URL", "Address","Region"])
    
    # Load existing processed hospitals
    existing_hospitals = set()
    try:
        df_existing = pd.read_csv(hospitalDetailFileName)
        existing_hospitals = set(df_existing["Hospital URL"])
    except:
        pass  # If file is missing, start fresh

    if driver is None :
        driver = get_driver()
    

    with open(hospitalDetailFileName, "a") as file:
        for _, row in df_hospitals.iterrows():
            state_name = row["State"]
            city_name = row["City"]
            hospital_name = row["Hospital Name"]
            hospital_url = row["Hospital URL"]

            if hospital_url in existing_hospitals:
                continue  # Skip already scraped hospitals















            address,phone,email,website,specialties,services = scrap_hospital_url(driver, hospital_name, hospital_url) 

            file.write(f"{state_name},{city_name},{hospital_name},{hospital_url},{address},{phone},{email},{website},{specialties},{services}\n")
            util.log_message(f"✅ Hospital details saved: {hospital_name}")

    driver.quit()
    util.log_message("🎉 Detailed hospital scraping completed!")

if __name__ == "__main__":
    scrape_hospital_details()
