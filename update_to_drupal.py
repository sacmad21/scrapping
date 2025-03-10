import requests
import json
from util import *
import pandas as pd
import os

# Drupal API Credentials
DRUPAL_URL = "https://your-drupal-site.com"
DRUPAL_USERNAME = "admin"
DRUPAL_PASSWORD = "password"

# Progress tracking file
UPLOAD_PROGRESS_FILE = "upload_progress.csv"

def get_auth_token():
    """Fetches CSRF token for secure API requests."""
    login_url = f"{DRUPAL_URL}/user/login?_format=json"
    payload = {"name": DRUPAL_USERNAME, "pass": DRUPAL_PASSWORD}
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(login_url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["csrf_token"]
    else:
        util.log_message("Error getting authentication token", "error")
        return None

def upload_data_to_drupal(data):
    """Uploads hospitals to Drupal, avoiding duplicates."""
    token = get_auth_token()
    if not token:
        return
    
    headers = {
        "Content-Type": "application/json",
        "X-CSRF-Token": token
    }

    uploaded_hospitals = util.load_progress(UPLOAD_PROGRESS_FILE)
    uploaded_names = {h["Name"] for h in uploaded_hospitals}

    for item in data:
        if item["Name"] in uploaded_names:
            util.log_message(f"Skipping {item['Name']} (already uploaded)")
            continue  # Skip already uploaded hospitals

        payload = {
            "type": [{"target_id": "hospital"}],
            "title": [{"value": item["Name"]}],
            "field_address": [{"value": item["Address"]}],
            "field_city": [{"value": item["City"]}],
            "field_state": [{"value": item["State"]}],
            "field_pincode": [{"value": item["Pincode"]}],
            "field_phone": [{"value": item["Phone"]}],
            "field_email": [{"value": item["Email"]}],
            "field_website": [{"uri": item["Website"]}],
            "field_specialties": [{"value": item["Specialties"]}],
            "field_num_beds": [{"value": item["Number of Beds"]}],
            "field_doctors": [{"value": item["Doctors"]}],
            "field_consultation_fee": [{"value": item["Consultation Fee"]}],
            "field_timings": [{"value": item["Timings"]}],
            "field_google_maps": [{"uri": item["Google Maps Link"]}]
        }

        response = requests.post(f"{DRUPAL_URL}/node?_format=json", headers=headers, json=payload)
        
        if response.status_code == 201:
            util.log_message(f"Successfully uploaded: {item['Name']}")
            uploaded_hospitals.append(item)
            util.save_to_csv(uploaded_hospitals, UPLOAD_PROGRESS_FILE)
        else:
            util.log_message(f"Failed to upload {item['Name']}: {response.text}", "error")

if __name__ == "__main__":
    if os.path.exists("hospitals_detailed.csv"):
        hospitals_data = pd.read_csv("hospitals_detailed.csv").to_dict(orient="records")
        upload_data_to_drupal(hospitals_data)
        util.log_message("All hospitals uploaded successfully!")
    else:
        util.log_message("Error: hospitals_detailed.csv not found!", "error")
