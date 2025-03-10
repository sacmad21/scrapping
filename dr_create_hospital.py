import requests
import json
import logging
from datetime import datetime


# === CONFIGURATION ===
DRUPAL_BASE_URL = "https://skyblue-echidna-761890.hostingersite.com"
USERNAME = "admin"
PASSWORD = "Admin@123"

# === LOGGING SETUP ===
log_filename = f"add_hospital_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    filename=log_filename,
    filemode="w",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# === LOGGING FUNCTION ===
def log(message, level="info"):
    """ Log messages to file and print them to the console. """
    if level == "debug":
        logging.debug(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    else:
        logging.info(message)
    
    print(message)


# === AUTHENTICATION FUNCTION ===
def get_auth_session():
    """ Authenticate with Drupal and get a session + CSRF token. """
    session = requests.Session()
    login_url = f"{DRUPAL_BASE_URL}/user/login?_format=json"
    csrf_token_url = f"{DRUPAL_BASE_URL}/session/token"
    
    log("🔄 Attempting to authenticate with Drupal...", "info")
    login_data = {"name": USERNAME, "pass": PASSWORD}
    
    try:
        response = session.post(login_url, json=login_data)
        if response.status_code == 200:
            log("✅ Authentication Successful!", "info")

            # Fetch CSRF Token
            log("🔄 Fetching CSRF Token...", "info")
            token_response = session.get(csrf_token_url)
            if token_response.status_code == 200:
                csrf_token = token_response.text.strip()
                log(f"✅ CSRF Token Retrieved: {csrf_token}", "info")
                session.headers.update({"X-CSRF-Token": csrf_token})
                return session
            else:
                log(f"❌ Failed to get CSRF Token. Status Code: {token_response.status_code}", "error")
                log(f"Response: {token_response.text}", "error")
                return None
        else:
            log(f"❌ Authentication Failed! Status Code: {response.status_code}", "error")
            log(f"Response: {response.text}", "error")
            return None
    except Exception as e:
        log(f"❌ ERROR: Exception occurred while authenticating: {str(e)}", "error")
        return None

# === FUNCTION TO ADD HOSPITAL ===
def add_hospital(session, hospital_data):
    """ Create a new hospital node in Drupal. """
    hospital_url = f"{DRUPAL_BASE_URL}/jsonapi/node/hospital"
    headers = {"Content-Type": "application/vnd.api+json"}

    payload = {
        "data": {
            "type": "node--hospital",
            "attributes": {
                "title": hospital_data["name"],
                "field_address": hospital_data["address"],
                "field_phone": hospital_data["phone"],
                "field_email": hospital_data["email"],
                "field_website": hospital_data["website"]
            }
        }
    }

    log(f"🔄 Attempting to add hospital: {hospital_data['name']}...", "info")
    
    response = session.post(hospital_url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        log(f"✅ Successfully added hospital: {hospital_data['name']}", "info")
    else:
        log(f"❌ Failed to add hospital: {hospital_data['name']}", "error")
        log(f"Response Code: {response.status_code}", "error")
        log(f"Response: {response.text}", "error")

# === SAMPLE HOSPITAL DATA ===
HOSPITALS = [
    {
        "name": "Apollo Hospital 10",
        "address": "123 Main Street, Mumbai",
        "phone": "+91 9876543210",
        "email": "info@apollo.com",
        "website": "https://apollo.com"
    }
]

# === RUN THE SCRIPT ===
if __name__ == "__main__":
    log("\n🚀 Starting Hospital Upload Process...", "info")
    
    session = get_auth_session()
    if session:
        for hospital in HOSPITALS:
            add_hospital(session, hospital)
    
    log("\n🎉 ALL HOSPITALS SUCCESSFULLY ADDED!", "info")
