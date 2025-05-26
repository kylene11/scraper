# Required Libraries
from selenium.webdriver.remote.webdriver import WebDriver
from browser_utils import extract_network_requests, create_driver
import time
from datetime import datetime
import json

def user_profile_scraper(browser: str, user_profile: str, headless: bool, url: str, author_id: str):

    '''
    Navigates to the user profile page. Collects the network response with the profile information. Parses the response for the required fields.

    Args:
        browser (str): The web browser to use (Tested on Chrome).
        user_profile (str): The user profile to use.
        headless (bool): Whether or not to run the browser in headless mode.
        url (str): Profile link.
        author_id (str): Input from database .
    '''

    driver = create_driver(browser, user_profile, headless)
    print("Driver created successfully!")

    # Open and Wait for page to load
    driver.get(url)
    print(f"Navigated to: {url}")
    time.sleep(5)

    profile = extract_network_requests(driver, keyword="UserByScreenName")

    try:
        user_data = profile[0]['data']['user']['result']
        legacy = user_data['legacy']
        
        # Convert to epoch integer
        created_at_str = user_data['core'].get("created_at")
        if created_at_str:
            created_at_epoch = int(datetime.strptime(created_at_str, "%a %b %d %H:%M:%S %z %Y").timestamp())
        else:
            print("⚠️ Warning: 'created_at' field is missing.")
            created_at_epoch = None
        output = {
            "scrape_ts": int(time.time()),
            "author_id": author_id,
            "platform": "Twitter",
            "platform_user_id": user_data.get("id"),
            "username": user_data['core'].get("screen_name"),
            "display_name": user_data['core'].get("name"),
            "url": url,
            "num_following": legacy.get("friends_count"),
            "num_followers": legacy.get("followers_count"),
            "num_favourites": legacy.get("favourites_count"),
            "user_bio": legacy.get("description"),
            
            "post_count": legacy.get("statuses_count"),
            "account_status": "Public" if user_data.get("privacy").get("protected") ==False else "Private",
            "default_profile_pic": False if legacy.get("default_profile_image") ==False else True,
           # "profile_pic_url": legacy.get("profile_image_url_https"),
           # "verified": legacy.get("verified"),
            "account_creation_date": created_at_epoch
        }

        return json.dumps(output, indent=2)
    
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def main():
    
    '''
    Tests the user_profile_scraper function. 
    '''

    # Variables
    browser = "Chrome"
    user_profile = "Default"
    headless = False

    url = "https://x.com/officialdbecks_"

    profile_data = user_profile_scraper(browser, user_profile, headless, url, author_id="12345")

    print(profile_data)
    
if __name__ == "__main__":
    main()