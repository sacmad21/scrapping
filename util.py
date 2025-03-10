import logging
import pandas as pd
import time
import random
import os
import re 

# Configure Logging
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_message(message, level="info"):
    """Logs messages with different levels."""
    if level == "info":
        logging.info(message)
    elif level == "warning":
        logging.warning(message)
    elif level == "error":
        logging.error(message)
    print(message)

def random_wait(min_sec=1, max_sec=10):
    """Wait for a random time between min_sec and max_sec."""
    wait_time = random.randint(min_sec, max_sec)
    log_message(f"Waiting for {wait_time} seconds...")
    time.sleep(wait_time)

def save_to_csv(data, filename):
    """Saves data to a CSV file."""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8')
    log_message(f"Data saved to {filename}")

def load_progress(filename):
    """Loads progress from a CSV file (if exists) to resume from failure."""
    if os.path.exists(filename):
        return pd.read_csv(filename).to_dict(orient="records")
    return []

def clean_data(text):
    """Cleans and formats scraped text."""
    if not text:
        return "N/A"
    
    # Remove extra spaces, newlines, and special characters
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII characters
    text = text.replace("\n", " ").replace("\r", " ")  # Remove newlines
    
    return text