import os
import pandas as pd
import util as util
from webscrapper import scrape_listing
from detailed_scraper import scrape_detailed
from update_to_drupal import upload_data_to_drupal

def test_scraper():
    """Runs the entire scraping workflow and checks output files."""
    util.log_message("Starting scraper test...")

    # Test 1: Run Listing Scraper
    util.log_message("Testing listing page scraper...")
    scrape_listing()
    assert os.path.exists("hospital_list.csv"), "❌ Test Failed: hospital_list.csv not found!"
    hospital_list = pd.read_csv("hospital_list.csv")
    assert not hospital_list.empty, "❌ Test Failed: hospital_list.csv is empty!"
    util.log_message("✅ Listing scraper test passed!")

    # Test 2: Run Detailed Scraper
    util.log_message("Testing detailed page scraper...")
    scrape_detailed()
    assert os.path.exists("hospitals_detailed.csv"), "❌ Test Failed: hospitals_detailed.csv not found!"
    detailed_data = pd.read_csv("hospitals_detailed.csv")
    assert not detailed_data.empty, "❌ Test Failed: hospitals_detailed.csv is empty!"
    util.log_message("✅ Detailed scraper test passed!")

    # Test 3: Validate Required Fields Exist
    required_columns = ["Name", "Address", "City", "State", "Phone", "Website"]
    missing_columns = [col for col in required_columns if col not in detailed_data.columns]
    assert not missing_columns, f"❌ Test Failed: Missing columns {missing_columns}!"
    util.log_message("✅ Data structure validation passed!")

    # Test 4: Upload a Few Records to Drupal (Dry Run)
    util.log_message("Testing Drupal upload (first 5 records)...")
    upload_data_to_drupal(detailed_data.to_dict(orient="records")[:5])
    util.log_message("✅ Drupal upload test passed!")

    util.log_message("🎉 All tests passed successfully!")

if __name__ == "__main__":
    test_scraper()
