import time
from common_utils import convert_to_epoch


def profile_parser(network_data):
    """
    Extracts profile information from the Twitter network request data.
    
    Parameters:
        network_data (dict): Parsed JSON from a Twitter network request (e.g., repost_data)

    Returns:
        list: A list of dictionaries, each containing structured profile information.
    """
    profiles = []

    try:
        instructions = network_data[0]['data']['user']['result']['timeline']['timeline']['instructions']
    except (KeyError, IndexError, TypeError) as e:
        print(f"[Error] Unable to parse network data structure: {e}")
        return []

    for instruction in instructions:
        if instruction.get("type") != "TimelineAddEntries":
            continue

        for entry in instruction.get("entries", []):
            if entry["content"].get("entryType") != "TimelineTimelineItem":
                continue

            try:
                user_result = entry["content"]["itemContent"]["user_results"]["result"]
                legacy = user_result.get("legacy", {})

                profile = {
                    "author_id": "None",
                    "platform": "Twitter",
                    "platform_user_id": user_result.get("id"),
                    "username": legacy.get("screen_name"),
                    "display_name": legacy.get("name"),
                    "url": f"https://x.com/{legacy.get('screen_name')}",
                    "num_friends": None,
                    "num_following": legacy.get("friends_count"),
                    "num_followers": legacy.get("followers_count"),
                    "user_bio": legacy.get("description"),
                    "scrape_ts": int(time.time()),
                    "post_count": legacy.get("media_count"),
                    "account_status": "Public" if legacy.get("description") else "Private",
                    "profile_pic_url": legacy.get("profile_image_url_https"),
                    "verified": legacy.get("verified"),
                    "account_creation_date": convert_to_epoch(legacy.get("created_at"))
                }

                profiles.append(profile)

            except Exception as e:
                print(f"[Warning] Failed to extract profile data from an entry: {e}")
                continue

    return profiles

def quotes_parser(network_data):
    authors = []
    tweets = []

    entries = network_data[0]["data"]["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"][0]["entries"]

    for entry in entries:
        try:
            tweet_result = entry["content"]["itemContent"]["tweet_results"]["result"]
            tweet_legacy = tweet_result["legacy"]
            tweet_view = tweet_result.get("views", {})

            author_result = tweet_result["core"]["user_results"]["result"]
            author_legacy = author_result["legacy"]

            author = {
                "author_id": "None",
                "platform": "Twitter",
                "platform_user_id": author_result.get("id"),
                "username": author_legacy.get("screen_name"),
                "display_name": author_legacy.get("name"),
                "url": f"https://x.com/{author_legacy.get('screen_name')}",
                "num_friends": None,
                "num_following": author_legacy.get("friends_count"),
                "num_followers": author_legacy.get("followers_count"),
                "user_bio": author_legacy.get("description"),
                "scrape_ts": int(time.time()),
                "post_count": author_legacy.get("media_count"),
                "account_status": "Public" if author_legacy.get("description") else "Private",
                "profile_pic_url": author_legacy.get("profile_image_url_https"),
                "verified": author_legacy.get("verified"),
                "account_creation_date": convert_to_epoch(author_legacy.get("created_at")),
            }

            tweet = {
                "post_id": "None",
                "platform": "Twitter",
                "url": f"https://x.com/{author_legacy.get('screen_name')}/status/{tweet_result.get('rest_id')}",
                "platform_pid": tweet_result.get("rest_id"),
                "post_type": tweet_legacy.get("entities", {}).get("media", [{}])[0].get("type", "text") if tweet_legacy.get("entities", {}).get("media") else "text",
                "post_title": "None",
                "post_author": author_legacy.get("screen_name"),
                "post_author_url": f"https://x.com/{author_legacy.get('screen_name')}",
                "content": tweet_legacy.get("full_text"),
                "content_url": [media["media_url_https"] for media in tweet_legacy.get("entities", {}).get("media", [])] if "media" in tweet_legacy.get("entities", {}) else "None",
                "post_datetime": convert_to_epoch(tweet_legacy.get("created_at")),
                "scrape_datetime": int(time.time()),
                "reaction_count": tweet_legacy.get("favorite_count"),
                "reaction_detail": "None",
                "comment_count": tweet_legacy.get("reply_count"),
                "share_count": tweet_legacy.get("retweet_count"),
                "view_count": tweet_view.get("count") if tweet_view else "None",
                "quote_count": tweet_legacy.get("quote_count"),
                "group_handle": "None",
                "group_url": "None",
            }

            authors.append(author)
            tweets.append(tweet)

        except Exception as e:
            print(f"Skipped an entry due to error: {e}")

    return authors, tweets


def repost_parser(network_data):
    reposters = []
    
    entries = network_data[0]["data"]["retweeters_timeline"]["timeline"]["instructions"][0]["entries"]

    for entry in entries:
        try:
            user_result = entry["content"]["itemContent"]["user_results"]["result"]
            legacy = user_result.get("legacy", {})

            profile = {
                "author_id": "None",
                "platform": "Twitter",
                "platform_user_id": user_result.get("id"),
                "username": legacy.get("screen_name"),
                "display_name": legacy.get("name"),
                "url": f"https://x.com/{legacy.get('screen_name')}",
                "num_friends": "None",
                "num_following": legacy.get("friends_count"),
                "num_followers": legacy.get("followers_count"),
                "user_bio": legacy.get("description"),
                "scrape_ts": int(time.time()),
                "post_count": legacy.get("media_count"),
                "account_status": "Public" if legacy.get("description") else "Private",
                "profile_pic_url": legacy.get("profile_image_url_https"),
                "verified": legacy.get("verified"),
                "account_creation_date": convert_to_epoch(legacy.get("created_at"))
            }

            reposters.append(profile)

        except Exception as e:
            print(f"Skipping entry due to error: {e}")
            continue

    return reposters


def metrics_parser(network_data):
    try:
        entry = network_data[0]["data"]["threaded_conversation_with_injections_v2"]["instructions"][0]["entries"][0]
        tweet_result = entry["content"]["itemContent"]["tweet_results"]["result"]
        tweet_legacy = tweet_result["legacy"]
        tweet_view = tweet_result.get("views", {})

        author_result = tweet_result["core"]["user_results"]["result"]
        author_legacy = author_result["legacy"]
        author_core = author_result["core"]

        author = {
            "scrape_ts": int(time.time()),
            "platform": "Twitter",
            "platform_user_id": author_result.get("rest_id"),
            "username": author_core.get("screen_name"),
            "display_name": author_core.get("name"),
            "url": f"https://x.com/{author_core.get('screen_name')}",
            
            "num_following": author_legacy.get("friends_count"),
            "num_followers": author_legacy.get("followers_count"),
            "user_bio": author_legacy.get("description"),
            
            "post_count": author_legacy.get("media_count"),
            "account_status": "Public" if author_result.get("privacy").get("protected") ==False else "Private",
            # "profile_pic_url": author_legacy.get("profile_image_url_https"),
            # "verified": author_legacy.get("verified"),
            "account_creation_date": convert_to_epoch(author_core.get("created_at")),
        }

        tweet = {
            
            "platform": "Twitter",
            "url": f"https://x.com/{author_core.get('screen_name')}/status/{tweet_result.get('rest_id')}",
            "platform_pid": tweet_result.get("rest_id"),
            "post_type": tweet_legacy.get("entities", {}).get("media", [{}])[0].get("type", "text") if tweet_legacy.get("entities", {}).get("media") else "text",
            #"post_title": "None",
            "post_author": author_core.get("screen_name"),
            "post_author_url": f"https://x.com/{author_core.get('screen_name')}",
            "content": tweet_legacy.get("full_text"),
            "content_url": [media["media_url_https"] for media in tweet_legacy.get("entities", {}).get("media", [])] if "media" in tweet_legacy.get("entities", {}) else "None",
            "post_datetime": convert_to_epoch(tweet_legacy.get("created_at")),
            "scrape_datetime": int(time.time()),
            "reaction_count": tweet_legacy.get("favorite_count"),
            #"reaction_detail": "None",
            "comment_count": tweet_legacy.get("reply_count"),
            "share_count": tweet_legacy.get("retweet_count"),
            "view_count": tweet_view.get("count") if tweet_view else "None",
            "quote_count": tweet_legacy.get("quote_count"),
            # "group_handle": "None",
            # "group_url": "None",
        }

        return author, tweet

    except Exception as e:
        print(f"Error parsing main post: {e}")
        return None, None