import subprocess
import multiprocessing
import time
import csv
import random

# === CONFIGURATION ===
NUM_PROCESSES = 100  # Total scrapers running in parallel
HOSPITAL_LIST_FILE = "hospitalList.csv"  # Input file with hospital URLs
PROXY_LIST_FILE = "proxies.txt"  # Proxy list file
SCRAPER_SCRIPT = "detailed_scrapper.py"  # Scraper script

# === FUNCTION TO LOAD HOSPITAL URLs ===
def load_hospital_urls():
    """Loads hospital URLs from CSV file."""
    urls = []
    with open(HOSPITAL_LIST_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 4:  # Ensure valid row format
                urls.append(row[3])  # Extract hospital URL
    return urls

# === FUNCTION TO LOAD PROXIES ===
def load_proxies():
    """Loads proxy list from file."""
    proxies = []
    with open(PROXY_LIST_FILE, "r") as file:
        proxies = [line.strip() for line in file.readlines()]
    return proxies

# === FUNCTION TO START SCRAPING PROCESS ===
def start_scraper(url, proxy):
    """Launches `detailed_scrapper.py` with hospital URL and proxy."""
    try:
        subprocess.run(
            ["python", SCRAPER_SCRIPT, url, proxy], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"⚠️ Error in process for {url}: {str(e)}")

# === FUNCTION TO MONITOR AND RESTART SCRAPERS ===
def scraper_worker(urls, proxies):
    """Manages parallel scrapers and restarts failed ones."""
    processes = []
    
    for i in range(NUM_PROCESSES):
        if not urls:
            break  # No more URLs to process

        url = urls.pop()
        proxy = random.choice(proxies)  # Assign a random proxy

        print(f"🚀 Starting scraper {i+1}/{NUM_PROCESSES} for {url} using {proxy}")
        
        p = multiprocessing.Process(target=start_scraper, args=(url, proxy))
        p.start()
        processes.append((p, url, proxy))

    # Monitor and restart failed processes
    while processes:
        for p, url, proxy in processes:
            if not p.is_alive():
                print(f"🔄 Restarting scraper for {url} with new proxy...")
                new_proxy = random.choice(proxies)
                p = multiprocessing.Process(target=start_scraper, args=(url, new_proxy))
                p.start()
                processes.append((p, url, new_proxy))

            time.sleep(2)  # Prevent CPU overuse

# === MAIN EXECUTION ===
if __name__ == "__main__":
    urls = load_hospital_urls()
    proxies = load_proxies()
    
    if not urls:
        print("⚠️ No hospital URLs found in hospitalList.csv.")
        exit()
    
    if len(proxies) < NUM_PROCESSES:
        print("⚠️ Not enough proxies for all processes! Consider adding more proxies.")
    
    scraper_worker(urls, proxies)
