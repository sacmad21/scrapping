import requests
import json
import logging
from datetime import datetime

# === CONFIGURATION ===
DRUPAL_BASE_URL = "https://skyblue-echidna-761890.hostingersite.com"
USERNAME = "admin"
PASSWORD = "Admin@123"

# === LOGGING SETUP ===
log_filename = f"add_hospital_fields_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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

# === FUNCTION TO ADD FIELD TO CONTENT TYPE ===
def add_field(session, field_name, field_type, field_label, bundle):
    """ Add a new field to a content type in Drupal. """
    field_url = f"{DRUPAL_BASE_URL}/admin/structure/types/manage/{bundle}/fields/add-field"
    headers = {"Content-Type": "application/vnd.api+json"}

    field_data = {
        "data": {
            "type": "field_config",
            "attributes": {
                "field_name": field_name,
                "entity_type": "node",
                "bundle": bundle,
                "label": field_label,
                "type": field_type,
            }
        }
    }

    log(f"🔄 Attempting to add field '{field_label}' to content type '{bundle}'...", "info")
    
    response = session.post(field_url, json=field_data, headers=headers)

    if response.status_code in [200, 201]:
        log(f"✅ Successfully added field '{field_label}' to '{bundle}'", "info")
    else:
        log(f"❌ Failed to add field '{field_label}' to '{bundle}'", "error")
        log(f"Response Code: {response.status_code}", "error")
        log(f"Response: {response.text}", "error")

# === HOSPITAL FIELDS ===
HOSPITAL_FIELDS = [
    {"name": "field_address", "type": "text", "label": "Address"},
    {"name": "field_state", "type": "entity_reference", "label": "State"},
    {"name": "field_city", "type": "entity_reference", "label": "City"},
    {"name": "field_phone", "type": "text", "label": "Phone Number"},
    {"name": "field_email", "type": "email", "label": "Email"},
    {"name": "field_website", "type": "link", "label": "Website URL"},
    {"name": "field_specialties", "type": "entity_reference", "label": "Specialties"},
    {"name": "field_services", "type": "entity_reference", "label": "Services"},
    {"name": "field_hospital_url", "type": "link", "label": "Hospital Profile URL"},
    {"name": "field_published", "type": "boolean", "label": "Published"},
]

# === RUN THE SCRIPT ===
if __name__ == "__main__":
    log("\n🚀 Starting Hospital Content Type Field Creation...", "info")
    
    session = get_auth_session()
    if session:
        for field in HOSPITAL_FIELDS:
            add_field(session, field["name"], field["type"], field["label"], "hospital")
    
    log("\n🎉 ALL FIELDS SUCCESSFULLY ADDED TO 'HOSPITAL' CONTENT TYPE!", "info")
