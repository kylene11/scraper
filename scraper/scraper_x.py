# Import necessary libraries
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from typing import Optional, Dict, Tuple
from browser_utils import extract_network_requests, create_driver
from common_utils import scroll_to_bottom, slow_type, create_json
from parser_utils import profile_parser, quotes_parser, repost_parser, metrics_parser
from dotenv import load_dotenv
from urllib.parse import urlparse
import time
from datetime import datetime
import logging
import os
import json

# Loading variables from .env file
load_dotenv()

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Log filename with timestamp
log_filename = os.path.join(
    "logs", datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
)

# Logging config
logging.basicConfig(
    filename=log_filename,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def log_in(driver: WebDriver, username: str, password: str, timeout: int = 35):

    '''
    Checks the login status and logs into the account if the login button is found in the page.

    Args:
        driver (WebDriver): An instance of Selenium WebDriver.
        username (str): The username of the Twitter account.
        password (str): The password of the Twitter account.
        timeout (int, optional): Time in seconds to wait for each element to be clickable. Defaults to 5.

    Returns:
        bool: True if the login attempt was initiated, False if the user is already logged in.
    '''

    try:

        wait = WebDriverWait(driver, timeout)

        # Check if Login button is present
        login_button = driver.find_element(By.XPATH, "//a[@data-testid='login']")
        logger.info("Login button found. Account not logged into.")

        # Click the Login button
        login_button.click()
        logger.info("Clicked Log in.")

        # Enter username
        username_field = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//label[.//span[text()='Phone, email, or username']]//input")
        ))
        slow_type(username_field, username)
        # username_field.send_keys(username)
        logger.info("Entered Username.")

        # Click Next
        next_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[text()='Next']]")
        ))
        next_button.click()
        logger.info("Clicked Next.")

        # Enter password
        password_field = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//label[.//span[text()='Password']]//input")
        ))
        slow_type(password_field, password)
        # password_field.send_keys(password)
        logger.info("Entered Password.")

        # Click Login
        submit_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[text()='Log in']]")
        ))
        submit_button.click()
        logger.info("Submitted login form.")

        logger.info("Logged in successfully.")
        return True

    except NoSuchElementException as e:
        logger.warning("Login button not found. Account is already logged in.")
        return False
    except TimeoutException as e:
        logger.error("Timeot waiting for an element: %s", e)
    except ElementClickInterceptedException as e:
        logger.error("Element click intercepted: %s", e)
    except Exception as e:
        logger.exception("Unexpected error during login: %s", e)

    return False


def metrics_author_details(driver: WebDriver) -> Optional[Tuple[Dict, Dict]]:
    
    '''
    Retrieves tweet metrics, author details, and tweet content from the network request containing 'TweetDetail'. Parses reterived response to optain author details and tweet content.
    
    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        author_id (str): Input from database.
    
    Returns:
        dict: Parsed JSON response from the PostDetail request, if found.
    '''

    # Use existing utility to get network data
    try:
        logger.info("Extracting metrics data...")
        metrics_data = extract_network_requests(driver, keyword="TweetDetail")
        with open("debug_raw_metrics.json", "w", encoding="utf-8") as f:
            json.dump(metrics_data, f, indent=2)
        logger.info("Parsing metrics data...")
        metrics_author, metrics_tweet = metrics_parser(metrics_data)

        logger.info("Successfully extracted author and tweet metrics.")
        return metrics_author, metrics_tweet

    except Exception as e:
        logger.exception("Error while extracting metrics: %s", e)
        return None

def post_engagement(driver: WebDriver, timeout: int = 5) -> bool:
    
    '''
    Navigates to the 'View Post Engagement' section of a tweet.
    
    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        timeout (int): Time to wait for elements to load.

    Returns:
        bool: True if successful, False otherwise.
    '''

    try:
        logger.info("Attempting to open view post engagement...")

        wait = WebDriverWait(driver, timeout)

        # Click the 3 dots
        three_dots_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@aria-label='More']")))
        three_dots_button.click()
        logger.info("Clicked the 3 dots.")

        # Click "View post engagements"
        view_engagement = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='View post engagements']]")))
        view_engagement.click()
        logger.info("Clicked 'View post engagements'.")

        # Wait for engagement modal
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//a[.//span[text()='Quotes']]")))
        logger.info("Engagement modal loaded successfully.")

        return True

    except TimeoutException as e:
        logger.warning("Timeout while trying to click view post engagements: %s", e)
    except Exception as e:
        logger.exception("Unexpected error in post_engagement: %s", e)

    return False

    

def quotes(driver: WebDriver) -> Optional[Tuple[Dict, Dict]]:
    
    '''
    Scrolls to the bottom of the quotes section and retrieves quote details using network logs.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
    '''

    try:
        logger.info("Scrolling to bottom to load quotes...")
        scroll_to_bottom(driver)

        logger.info("Extracting quote data...")
        quote_data = extract_network_requests(driver, keyword="SearchTimeline")

        logger.info("Parsing quote tweet data...")
        quote_profile_parsed, quote_tweet_parsed = quotes_parser(quote_data)

        logger.info("Successfully extracted and parsed quote data.")
        return quote_profile_parsed, quote_tweet_parsed

    except Exception as e:
        logger.exception("Failed to extract or parse quote tweets: %s", e)
        return None

def reposts(driver: WebDriver, timeout: int = 5):

    '''
    Scrolls to the bottom of the reposters section and retrieves retweet details using network logs.

    Args:
        driver (Webdriver): The Selenium WebDriver instance.
    '''
    try:
        logger.info("Opening 'Reposts' tab...")
        wait = WebDriverWait(driver, timeout)

        reposts_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Reposts']]")
        ))
        reposts_tab.click()

        logger.info("Scrolling to bottom to load reposters...")
        scroll_to_bottom(driver)

        logger.info("Extracting repost data...")
        repost_data = extract_network_requests(driver, keyword="Retweeters")
        repost_parsed = repost_parser(repost_data)

        logger.info("Successfully extracted repost data.")
        return repost_parsed

    except TimeoutException:
        logger.warning("Timeout when clicking the Reposts tab.")
    except NoSuchElementException:
        logger.warning("Could not locate Reposts tab.")
    except Exception as e:
        logger.exception("Unexpected error in reposts(): %s", e)

    return None
    
def following(driver: WebDriver, timeout: int = 5):

    '''
    Scrolls to the bottom of the following section and retrieves following details using network logs.

    Args:
        driver (Webdriver): The Selenium WebDriver instance.
    '''

    try:
        logger.info("Opening 'Following' tab...")
        wait = WebDriverWait(driver, timeout)

        following_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Following']]")
        ))
        following_tab.click()

        logger.info("Scrolling to bottom to load following...")
        scroll_to_bottom(driver)

        logger.info("Extracting following data...")
        following_data = extract_network_requests(driver, keyword="Following")
        following_parsed = profile_parser(following_data)

        logger.info("Successfully extracted following data.")
        return following_parsed

    except TimeoutException:
        logger.warning("Timeout when clicking the Following tab.")
    except Exception as e:
        logger.exception("Unexpected error in following(): %s", e)

    return None

def followers(driver: WebDriver, timeout: int = 5):

    '''
    Scrolls to the bottom of the followers section and retrieves followers details using network logs.

    Args:
        driver (Webdriver): The Selenium WebDriver instance.   
    '''

    try:
        logger.info("Opening 'Followers' tab...")
        wait = WebDriverWait(driver, timeout)

        followers_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[.//span[text()='Followers']]")
        ))
        followers_tab.click()

        logger.info("Scrolling to bottom to load followers...")
        scroll_to_bottom(driver)

        logger.info("Extracting followers data...")
        followers_data = extract_network_requests(driver, keyword="Followers")
        followers_parsed = profile_parser(followers_data)

        logger.info("Successfully extracted followers data.")
        return followers_parsed

    except TimeoutException:
        logger.warning("Timeout when clicking the Followers tab.")
    except Exception as e:
        logger.exception("Unexpected error in followers(): %s", e)

    return None



def main():

    '''
    Runs the scraping process given a tweet link
    '''

    # Credentials
    username = os.getenv("MY_USERNAME")
    password = os.getenv("PASSWORD")
    browser = os.getenv("BROWSER")
    user_profile = os.getenv("USER_PROFILE")

    # Url handling
    tweet_url = "https://x.com/stillgray/status/1923976708941807791"

    parsed_url = urlparse(tweet_url)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) >= 1:
        profile_url = f"https://x.com/{path_parts[0]}"

    # Creating browser
    driver = create_driver(browser, user_profile, False)
    print("Driver created successfully")

    # Load tweet
    driver.get(tweet_url)

    time.sleep(5)
    
    # Check log in
    check_login = log_in(driver, username, password)
    print("Checked log in.")

    # Reload url if log is true
    if check_login:
        driver.get(tweet_url)
        time.sleep(5)
            
    # Collect Tweet metrics and Author info
    metrics_profile_result, metrics_tweet_result = metrics_author_details(driver)
    create_json("testing_2//test_metrics_author.json", metrics_profile_result)
    create_json("testing_2//test_metrics_tweet.json", metrics_tweet_result)
    print("Collected Tweet metrics and Author info.")
    

    # # Switch to mentions
    # post_engagement(driver)

    # # Collect quotes
    # quotes_profile_result, quotes_tweet_result = quotes(driver)
    # create_json("testing_2//test_quotes_profile.json", quotes_profile_result)
    # create_json("testing_2//test_quotes_tweet.json", quotes_tweet_result)
    # print("Collected quotes.")

    # # Collect reposts
    # reposts_result = reposts(driver)
    # create_json("testing_2//test_reposts.json", reposts_result)
    # print("Collected reposters.")

    # # Switch to user profile
    # driver.get(profile_url)
    # time.sleep(4)

    # # Collect following
    # following_result = following(driver)
    # create_json("testing_2//test_following.json", following_result)
    # print("Collected following.")

    # # Collect followers
    # followers_result = followers(driver)
    # create_json("testing_2//test_followers.json", followers_result)
    # print("Collected followers.")

    # Quit driver
    driver.quit()

if __name__ == "__main__":
    main()