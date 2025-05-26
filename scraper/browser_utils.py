"""
Utils for creating Chrome Webdriver using Selenium.
Modify CHROMEDRIVER_PATH, USER_DATA_DIR & USER_PROFILES for respective system.

Update 22 Aug 2023: Has been edited for inclusion of Firefox (Instagram) and Edge (Tiktok).
"""
import asyncio
import random
import time
import os

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver import Chrome, Edge, Firefox
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions

from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile

from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from typing import Literal, Union


import logging
import json

logger = logging.getLogger(__name__)


# Global lock as only one chromedriver can be open at any time
CHROME_LOCK = asyncio.Lock()

SUPPORTED_BROWSERS = ["Chrome", "Firefox", "Edge"]
Browser_Type = Literal[*SUPPORTED_BROWSERS] 

def create_driver(
        browser_type: Browser_Type, user_profile: str = "Default", headless: bool = False
    ) -> WebDriver:
    """
    Create a selenium driver based on the browser type. User profile can be specified based on the avatar.
    
    How to get user profile:
        Firefox: Go to about:profiles in firefox
        Chrome: Go to chrome://version/ in Chrome
        Edge: Go to edge://version/ in Edge
    
    Args:
        browser_type (Literal["Chrome", "Firefox"]): The type of browser to create a driver for.
        user_profile (str, optional): The user profile to use. Defaults to "Default".
        headless (bool, optional): Whether or not to run the browser in headless mode. Defaults to False.
        
    Returns:
        WebDriver: The created selenium driver.
        
    Raises:
        ValueError: If the browser type is not supported.
    """
    if browser_type not in SUPPORTED_BROWSERS:
        raise ValueError(f"No {browser_type} found. Browser type must be either Chrome or Firefox or Edge.")
    
    computer_username = os.environ.get("USER")

    try:
        # Create a firefox driver object
        if browser_type == "Firefox":
            print("Creating Firefox Driver")
            firefox_profile_dir = rf'/home/{computer_username}/.mozilla/firefox/{user_profile}'
            
            ser = FirefoxService()
            op = FirefoxOptions()
            op = set_common_options(op, browser_type, headless=headless)
            print(f"firefox_profile_dir: {firefox_profile_dir}")
            op.add_argument(rf"--profile={firefox_profile_dir}")
            
            driver = Firefox(service=ser, options=op)
            driver = post_driver_configuration(driver)
            return driver

        # create an edge driver object
        elif browser_type == "Edge":
            print("Creating Edge Driver")
            edge_data_dir = rf'/home/{computer_username}/.config/microsoft-edge/{user_profile}'

            # Edge
            ser = EdgeService()
            op = EdgeOptions()
            op = set_common_options(op, browser_type, headless=headless)
            
            op.add_argument(rf"user-data-dir={edge_data_dir}")
            op.set_capability("ms:loggingPrefs", {"performance": "ALL"})  
            
            driver = Edge(service=ser, options=op)
            driver = post_driver_configuration(driver)
            
            return driver
        
        # create a chrome driver object
        elif browser_type == "Chrome":
            print("Creating Chrome Driver")
            chrome_data_dir = rf'/home/{computer_username}/.config/google-chrome'

            ser = ChromeService()
            op = ChromeOptions()
            op = set_common_options(op, browser_type, headless=headless)
            op.set_capability("goog:loggingPrefs", {"performance": "ALL"}) 

            # Set to specified user profile if passed in
            op.add_argument(rf"user-data-dir={chrome_data_dir}")
            op.add_argument(rf"--profile-directory={user_profile}")
            try:
                driver = Chrome(service=ser, options=op)
            except:
                try:
                    driver = Chrome(
                        service=ChromeService(ChromeDriverManager().install()),
                        options=op,
                    )

                except:
                    print("Please close all chrome browsers")
                    # exit()
            driver = post_driver_configuration(driver)
            return driver

        else:
            logger.error(f"Could not find browser type: {browser_type}. Browser type must be one of: chrome, firefox or edge. Returning None for driver")
            raise WebDriverException("Could not find browser type. Browser type must be one of: chrome, firefox or edge.")
            
    except WebDriverException as e:
        logger.exception(
            "WebDriverException when creating Webdriver. Ensure all browsers are closed."
        )
        logger.exception(e)
        return None

def set_common_options(options: Union[ChromeOptions, FirefoxOptions, EdgeOptions], browser_type: Browser_Type, headless: bool):
    """
    Common options for all browsers. 
    Args:
        options (Union[ChromeOptions, FirefoxOptions]): Options object for the browser
    Returns:
        Union[ChromeOptions, FirefoxOptions]: Updated options object for the browser
    """
    if headless:
        options.add_argument("--headless=new")
    
    # Common settings for all browsers.
    options.page_load_strategy = 'normal' # normal, eager, none. This allows the page to load fully before returning.
    options.add_argument("--disable-blink-features=AutomationControlled") # This disables the automation control flag.
    options.add_argument('--start-maximized') # This starts the browser in full screen mode.
    options.add_argument('--disable-dev-shm-usage') # This disables the shared memory usage.
    options.add_argument('--no-sandbox') # This disables the sandbox.
    options.add_argument('--disable-gpu') # This disables the GPU.
    options.add_argument('--disable-notifications') # This disables the notifications.
    options.add_argument('--disable-popup-blocking') # This disables the popup blocking.
    options.add_argument("--disable-notifications") # This disables the notifications.
    options.add_argument("--disable-infobars") # This disables the infobars.

    # Common settings but catered to specific browser types.
    if browser_type == "Chrome" or browser_type == "Edge":
        options.add_experimental_option('useAutomationExtension', False) # This disables the automation extension.
        options.add_experimental_option("excludeSwitches", ["enable-automation"]) # This excludes the automation switch.
    elif browser_type == "Firefox":
        options.set_preference("useAutomationExtension", False) # This disables the automation extension.
        options.set_preference("dom.webdriver.enabled", False) # This disables the webdriver.
    else:
        print("No setting options for this browser type")
   
    return options

def post_driver_configuration(driver: WebDriver):
    """
    Configuration to be done after the driver is created. This is to prevent bot detection.
    Args:
       options (Options): Browser options to configure
    """

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_cdp_cmd("Network.enable", {})

    return driver


def extract_network_requests(driver: WebDriver, keyword: str = None):
    """
    Extracts network requests from the browser's performance logs.
    Args:
        driver (WebDriver): The WebDriver instance.
        keyword (str, optional): A keyword to filter the URLs. Defaults to None.

    Returns:
        list: A list of network response data for the filtered requests (or all if no keyword is provided).
    """
    logs = driver.get_log("performance")
    responses = []

    for log in logs:
        try:
            log_json = json.loads(log["message"])["message"]
            if log_json["method"] == "Network.responseReceived":
                request_id = log_json["params"]["requestId"]
                url = log_json["params"]["response"]["url"]
                
                if keyword is None or keyword in url:
                    logger.info(f"Request URL: {url}")
                    response_body = driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
                    try:
                        response_data = json.loads(response_body["body"])
                    except json.JSONDecodeError as e:
                        multiple_json_part = response_body["body"].strip().split("\n")
                        # Parse each JSON part and add "request_url"
                        multi_json = [
                            {**json.loads(part), "request_url": url}  # Merge dict with new key
                            for part in multiple_json_part if part.strip()
                        ]
                        response_data = {"multi_line_data": multi_json} 
                        responses.append(response_data)
                    except Exception as e:
                        print(f"extraction error {e}")
                    else:
                        response_data["request_url"] = url
                        responses.append(response_data)
        except Exception as e:
            # logger.exception(f"Error processing log entry: {e}")
            pass

    return responses


def test_create_driver(browser: str, user_profile: str, headless: bool=False, url: str="https://www.google.com"):
    """
    Test case for create_driver. Creates a driver and navigates to google.com. Quits after 5 seconds.
    Args:
       browser (str): Browser to test
       headless (bool): Whether to run headless or not
    """
    try:
        driver = create_driver(browser, user_profile=user_profile, headless=headless)
    except Exception as e:
        print(f"Failed to create driver: {e}")
    else:
        print(f"driver returned: {type(driver)}")
        print(f"driver url: {driver.current_url}, given url: {url}")
        time.sleep(1)
        driver.get(url)
        time.sleep(5)
        driver.quit()

def main():
    """
    Tests the create_driver function
    """
    print("Testing create_driver")
    browser_list = [
        {
            "browser": "Chrome",
            "user_profile": "Default",
            "url": "https://www.google.com/"
        },
    ]
    
    
    for browser in browser_list:
        test_create_driver(browser["browser"], browser["user_profile"], False, browser["url"])

if __name__ == "__main__":
    main()