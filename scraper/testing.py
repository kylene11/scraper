# Import necessary libraries
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from typing import Optional, Dict
from browser_utils import extract_network_requests, create_driver
from common_utils import create_json
from scraper_x import log_in, post_engagement, quotes, metrics_author_details, reposts, following, followers
import time
import json
    
def test_login(browser: str, user_profile: str, username: str, password: str, headless: bool = False, url: str = "https://www.google.com"):
    """
    Test case for login. Creates a driver and logs in to the account. Navigates to given URL and quits.

    Args:
        browser (str): Browser to test
        user_profile (str): User profile name
        username (str): Username for login
        password (str): Password for login
        headless (bool): Whether to run headless or not
        url (str): URL to navigate to after login
    """
    try:
        driver = create_driver(browser, user_profile=user_profile, headless=headless)
        print("Driver created successfully.")
        
        logged_in = log_in(driver, username, password)
        if logged_in:
            print("Login successful.")
        else:
            print("Login skipped or already logged in.")

        driver.get(url)
        print(f"Navigated to: {driver.current_url}")
        time.sleep(5)

    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
            print("Driver closed.")


def test_metrics(browser: str, user_profile: str, headless: bool = False, url: str = "https://www.google.com", output_path: str = "tweet_details.json"):
    """
    Opens the driver, waits for TweetDetail request, and saves it to a JSON file.

    Args:
        driver (WebDriver): Selenium WebDriver instance (already initialized and logged in if required).
        output_path (str): Path to save the JSON output.
    """
    driver = create_driver(browser, user_profile=user_profile, headless=headless)
    print("Driver created successfully.")

    driver.get(url)
    print(f"Navigated to: {url}")

    print("Check login status.")
    log_in(driver, "mfirewalker17", "MF@firewalker17")

    print("Waiting for network traffic...")
    time.sleep(5)

    print("Extracting TweetDetail data...")
    result = metrics_author_details(driver)

    print(result)
    driver.quit()

    '''
    if result:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"TweetDetail data saved to: {output_path}")
    else:
        print("Failed to extract TweetDetail data.")
    '''


def test_quotes(browser: str, user_profile: str, headless: bool = False, url:str = "https://www.google.com"):
    
    driver = create_driver(browser, user_profile=user_profile, headless=headless)
    print("Driver created successfully.")

    driver.get(url)
    print(f"Navigated to: {url}")

    username = "mfirewalker17" 
    password = "MF@firewalker17"

    log_in(driver, username, password)
    print(driver.current_url)

    # driver.get(url)
    # print(f"Navigated to: {url}")

    print("Waiting for network traffic...")
    time.sleep(5)

    print("Extracting Quotes data...")
    quotes_result = quotes(driver)

    create_json("quotes.json", quotes_result)
    driver.quit()


def test_reposts(browser: str, user_profile: str, headless: bool = False, url:str = "https://www.google.com"):
    
    driver = create_driver(browser, user_profile=user_profile, headless=headless)
    print("Driver created successfully.")

    driver.get(url)
    print(f"Navigated to: {url}")

    username = "mfirewalker17" 
    password = "MF@firewalker17"

    log_in(driver, username, password)
    print(driver.current_url)

    # driver.get(url)
    # print(f"Navigated to: {url}")

    print("Waiting for network traffic...")
    time.sleep(5)

    print("Extracting Reposts data...")
    reposts_result = reposts(driver)

    create_json("reposts.json", reposts_result)
    driver.quit()


def test_following(browser: str, user_profile: str, headless: bool = False, url:str = "https://www.google.com"):
    
    driver = create_driver(browser, user_profile=user_profile, headless=headless)
    print("Driver created successfully.")

    driver.get(url)
    print(f"Navigated to: {url}")

    username = "mfirewalker17" 
    password = "MF@firewalker17"

    log_in(driver, username, password)
    print(driver.current_url)

    # driver.get(url)
    # print(f"Navigated to: {url}")

    print("Waiting for network traffic...")
    time.sleep(5)

    print("Extracting Following data...")
    following_result = following(driver)

    create_json("following.json", following_result)
    driver.quit()


def test_followers(browser: str, user_profile: str, headless: bool = False, url:str = "https://www.google.com"):
    
    driver = create_driver(browser, user_profile=user_profile, headless=headless)
    print("Driver created successfully.")

    driver.get(url)
    print(f"Navigated to: {url}")

    username = "mfirewalker17" 
    password = "MF@firewalker17"

    log_in(driver, username, password)
    print(driver.current_url)

    # driver.get(url)
    # print(f"Navigated to: {url}")

    print("Waiting for network traffic...")
    time.sleep(5)

    print("Extracting Followers data...")
    followers_result = followers(driver)

    create_json("followers.json", followers_result)
    driver.quit()


def main():
    """
    Runs test_login for specified browser configurations.
    """
    print("Testing login functionality")

    browser_list = [
        {
            "browser": "Chrome",
            "user_profile": "Default",
            "url": "https://x.com/viraf0753/following"
        },
    ]


    for browser_config in browser_list:
        test_followers(
            browser=browser_config["browser"],
            user_profile=browser_config["user_profile"],
            headless=False,
            url=browser_config["url"]
        )


if __name__ == "__main__":
    main()
