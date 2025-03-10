import subprocess
import multiprocessing
import time
import csv
import random

# === CONFIGURATION ===
NUM_PROCESSES = 100  # Total scrapers running in parallel
HOSPITAL_LIST_FILE = "data/hospitals/hl_0.csv"  # Input file with hospital URLs
PROXY_LIST_FILE = "proxies.txt"  # Proxy list file
SCRAPER_SCRIPT = "detailed_scrapper_with_proxy.py"  # Scraper script
COMMAND = "/home/devzone/MyCenter/genAIProj/llamaWork/scrap_sites/.venv/bin/python"


# === FUNCTION TO LOAD HOSPITAL URLs ===
def load_hospital_urls():
    """Loads hospital URLs from CSV file."""
    urls = []
    names = []
    with open(HOSPITAL_LIST_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) >= 5:  # Ensure valid row format
                urls.append(row[4])  # Extract hospital URL
                names.append(row[3]) 
    return names, urls




# === FUNCTION TO LOAD PROXIES ===
def load_proxies():
    """Loads proxy list from file."""
    proxies = []
    with open(PROXY_LIST_FILE, "r") as file:
        proxies = [line.strip() for line in file.readlines()]
    return proxies




# === FUNCTION TO START SCRAPING PROCESS ===
def start_scraper(name, url, proxy):
    """Launches `detailed_scraper.py` with hospital URL and proxy and logs output."""
    log_file = "proxy_scrapper_manager.log"

    try:
        with open(log_file, "a") as log:
            log.write(f"✅ Initiating Scraper : {name}, {url}, {proxy}\n")
            log.write("--------------------------------------------------\n")
            
            # Run the scraper and capture logs
            subprocess.run(
                [COMMAND, SCRAPER_SCRIPT, name, url, proxy], 
                stdout=log,  # Redirect stdout to log file
                stderr=log   # Redirect stderr to log file
            )
    except Exception as e:
        with open(log_file, "a") as log:
            log.write(f"⚠️ Error in process for {url}: {str(e)}\n")

    print(f"🔹 Scraper for {url} started, logs written to {log_file}")




# === FUNCTION TO MONITOR AND RESTART SCRAPERS ===
def scraper_worker(names, urls, proxies):
    """Manages parallel scrapers and restarts failed ones."""
    processes = []
    
    for i in range(NUM_PROCESSES):
        if not urls:
            break  # No more URLs to process

        url = urls.pop()
        name = names.pop()
        proxy = random.choice(proxies)  # Assign a random proxy


        print(f"🚀 Starting scraper {i+1}/{NUM_PROCESSES} for {url} using {proxy}")
        
        p = multiprocessing.Process(target=start_scraper, args=(name, url,proxy))
        p.start()
        processes.append((p, name, url, proxy))


    # Monitor and restart failed processes
    while processes:
        for p, name, url, proxy in processes:
            if not p.is_alive():
                print(f"🔄 Restarting scraper for {url} with new proxy.... ")
                new_proxy = random.choice(proxies)
                p = multiprocessing.Process(target=start_scraper, args=(name, url, new_proxy))
                # p.start()

                processes.append((p, name, url, new_proxy))

            time.sleep(2)  # Prevent CPU overuse

# === MAIN EXECUTION ===
if __name__ == "__main__":
    names, urls = load_hospital_urls()
    
    proxies = load_proxies()
    
    if not urls:
        print("⚠️ No hospital URLs found in hospitalList.csv.")
        exit()
    
    if len(proxies) < NUM_PROCESSES:
        print("⚠️ Not enough proxies for all processes! Consider adding more proxies.")
    
    scraper_worker(names, urls, proxies)
