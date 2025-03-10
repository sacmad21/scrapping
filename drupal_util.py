
# === CONFIGURATION ===
DRUPAL_BASE_URL = "https://skyblue-echidna-761890.hostingersite.com"
USERNAME = "admin"
PASSWORD = "Admin@123"

import requests
import json
import logging
from datetime import datetime

# === LOGGING SETUP ===
log_filename = f"add_taxonomy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
    
    # Authenticate user
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

# === FUNCTION TO CREATE TAXONOMY TERM ===
def create_taxonomy_term(session, vocabulary, term_name):
    """ Create a new term in an existing taxonomy vocabulary in Drupal. """
    taxonomy_url = f"{DRUPAL_BASE_URL}/jsonapi/taxonomy_term/{vocabulary}"
    headers = {
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json",
    }

    term_data = {
        "data": {
            "type": f"taxonomy_term--{vocabulary}",
            "attributes": {
                "name": term_name
            }
        }
    }

    log(f"🔄 Attempting to add term '{term_name}' to vocabulary '{vocabulary}'...", "info")

    response = session.post(taxonomy_url, json=term_data, headers=headers)

    if response.status_code in [200, 201]:
        log(f"✅ Successfully added term '{term_name}' to '{vocabulary}'", "info")
    elif response.status_code == 403:
        log(f"❌ Failed to add term '{term_name}' - Forbidden (403). CSRF Token might be missing.", "error")
        log(f"Response: {response.text}", "error")
    else:
        log(f"❌ Failed to add term '{term_name}' to '{vocabulary}'", "error")
        log(f"Response Code: {response.status_code}", "error")
#        log(f"Response: {response.text}", "error")

# === BULK UPLOAD FUNCTION ===
def add_terms_to_taxonomy(vocabulary_name, terms):
    """ Adds terms to an existing taxonomy vocabulary. """
    log(f"\n🔹 STARTING BULK UPLOAD: Adding terms to '{vocabulary_name}'", "info")
    session = get_auth_session()
    
    if not session:
        log("🚨 ERROR: Unable to authenticate. Aborting bulk upload.", "error")
        return

    for index, term in enumerate(terms, start=1):
        log(f"➡️ {index}/{len(terms)}: Processing term '{term}'...", "debug")
        create_taxonomy_term(session, vocabulary_name, term)

    log(f"✅ BULK UPLOAD COMPLETE: '{vocabulary_name}' vocabulary updated.", "info")

# === TAXONOMY DATA ===
TAXONOMIES = {
    "states": ["Maharashtra", "Delhi", "Karnataka", "Tamil Nadu", "West Bengal"],
    "cities": ["Mumbai", "Pune", "Bangalore", "Chennai", "Kolkata"],
    "medical_specialties": ["Cardiology", "Neurology", "Pediatrics", "Orthopedics"],
    "hospital_services": ["Emergency", "OPD", "Surgery", "24x7 Pharmacy"]
}

# === RUN THE SCRIPT ===
if __name__ == "__main__":
    log("\n🚀 Starting Taxonomy Upload Process...", "info")
    
    for vocab_name, terms in TAXONOMIES.items():
        add_terms_to_taxonomy(vocab_name, terms)
    
    log("\n🎉 ALL TAXONOMIES SUCCESSFULLY UPDATED!", "info")
