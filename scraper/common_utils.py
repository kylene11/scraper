from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from datetime import datetime
import hashlib
import random
import time
import json

def create_base_post_id(dashboard_id: int, query: str, batch_time: int):
    """
    Generates a unique ID using a hash of the given ID and query, combined with the current Unix timestamp.
    
    Args:
        dashboard_id (int): The external identifier.
        query (str): The input link to be hashed.
    
    Returns:
        str: A unique ID in the format "hash_currentUnixTimestamp"
    """
    combined_string = str(dashboard_id) + query  # Combine external ID and link
    hash_object = hashlib.sha256(combined_string.encode())  # Create SHA-256 hash
    hash_hex = hash_object.hexdigest()[:10]  # Take first 10 characters of the hash for uniqueness
    batch_time_str = str(batch_time)
    hash_tag = f"{hash_hex}_{batch_time_str}"
    
    return hash_tag


def extract_key(data, key):
    """
    Recursively search for a key in a nested JSON and return its value if found.
    
    Args:
        data (dict or list): The JSON object to search.
        key (str): The key to find.
    
    Returns:
        The value associated with the given key or None if not found.

    """
    if isinstance(data, dict):
        if key in data:
            return data[key]  # Return value if key is found
        for value in data.values():
            result = extract_key(value, key)
            if result is not None:
                return result  # Return the first occurrence found
    elif isinstance(data, list):
        for item in data:
            result = extract_key(item, key)
            if result is not None:
                return result
    return None  # Return None if key is not found


def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def create_json(file_path,  json_content):
    with open(file_path, 'w') as json_file:
        json.dump(json_content, json_file, indent=2)


def slow_type(element: WebElement, text: str, delay: tuple = (0.1, 0.3)):
    """Send a text to an element one character at a time with a delay."""
    for character in text:
        element.send_keys(character)
        time.sleep(random.uniform(*delay))


def scroll_to_bottom(driver: WebDriver, max_scrolls: int = 1, pause_range: tuple = (1, 4)):
    """
    Scrolls down the page to load dynamic content with random short pauses.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        max_scrolls (int): Max number of scroll actions to avoid infinite scrolling.
        pause_range (tuple): Range of pause time (in seconds) between scrolls.
    """
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(*pause_range))

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    print("Scrolling completed.")

def convert_to_epoch(created_at_str: str):
    '''
    Coverts the Account/Post creation date and time to epoch intergers
    '''
    created_at_epoch = int(datetime.strptime(created_at_str, "%a %b %d %H:%M:%S %z %Y").timestamp())

    return created_at_epoch
