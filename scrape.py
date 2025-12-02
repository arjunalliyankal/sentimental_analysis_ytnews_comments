import os
import sys
import csv
import demoji
import unicodedata
import re
import html
import time  # For implementing rate limiting
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

load_dotenv()
# YouTube Data API key (read from environment)
API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "YOUTUBE_API_KEY not set. Add it to your .env file at the project root or set the environment variable."
    )
    
    
    


def get_comments(client, video_id, page_token=None):
    try:
        response = (
            client.commentThreads()
            .list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,
                pageToken=page_token,
            )
            .execute()
        )
        return response
    except (HttpError, Exception) as e:
        raise e
    
def get_reply_comments(client, comment_id, token=None):
    try:
        response = (
            client.comments()
            .list(
                part="snippet",
                parentId=comment_id,
                textFormat="plainText",
                maxResults=100,
                pageToken=token,
            )
            .execute()
        )
        return response
    except HttpError as e:
        print("HTTP Error:", e)
        return None
    except Exception as e:
        print("Error:", e)
        return None


# ---------- helper cleaning functions you provided (merged & corrected) ----------

def remove_emoji(inputString: str) -> str:
    """Remove all emoji characters using demoji."""
    if not inputString:
        return ""
    dem = demoji.findall(inputString)
    for item in list(dem.keys()):
        inputString = inputString.replace(item, '')
    return inputString

def remove_non_english(inputString: str) -> str:
    """
    Keep only ASCII letters (A-Za-z), digits and space characters.
    This is a corrected/robust version of your provided function.
    It normalizes Unicode then filters to ASCII letters/digits/spaces.
    """
    if not inputString:
        return ""
    normalized = unicodedata.normalize('NFKD', inputString)
    filtered_chars = []
    for c in normalized:
        # keep ASCII letters, digits or whitespace
        if ord(c) < 128 and (c.isalpha() or c.isdigit() or c.isspace()):
            filtered_chars.append(c)
        # else drop character
    return ''.join(filtered_chars)

def remove_long_white_spaces(inputString: str) -> str:
    """Collapse any run of whitespace (tabs/newlines/multi-spaces) to a single space."""
    if not inputString:
        return ""
    return re.sub(r'\s+', ' ', inputString).strip()

# ---------- central cleaning pipeline ----------

def clean_comment(text: str) -> str:

    if not text:
        return ""
    
    s = html.unescape(str(text))
    s = remove_emoji(s)
    s = remove_non_english(s)
    s = remove_long_white_spaces(s)

    return s


def get_main_comment_text(item):
        """Safely extract top-level comment text from a comment thread item."""
        try:
            return item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        except Exception:
            return item.get("snippet", {}).get("textDisplay", "")

def get_reply_text(item):
    """Safely extract reply comment text."""
    try:
        return item["snippet"]["textDisplay"]
    except Exception:
        return item.get("snippet", {}).get("textDisplay", "")


def main(video_id):

    yt = build("youtube", "v3", developerKey=API_KEY)

    # Fetch top-level comment threads
    comments = []
    next_token = None
    while True:
        resp = get_comments(yt, video_id, next_token)  # your existing function
        if not resp:
            break
        comments.extend(resp.get("items", []))
        next_token = resp.get("nextPageToken")
        if not next_token:
            break
        time.sleep(1)

    # Fetch replies for each thread
    reply_comments = []
    for c in comments:
        reply_token = None
        while True:
            resp = get_reply_comments(yt, c["id"], reply_token)  # your existing function
            if not resp:
                break
            reply_comments.extend(resp.get("items", []))
            reply_token = resp.get("nextPageToken")
            if not reply_token:
                break
            time.sleep(1)

    # ---------- BUILD final variable: all_cleaned_comments ----------

    
    all_cleaned_comments = []

    # add cleaned main comments
    for t in comments:
        raw = get_main_comment_text(t)
        cleaned = clean_comment(raw)
        if cleaned:
            all_cleaned_comments.append(cleaned)

    # add cleaned reply comments
    for r in reply_comments:
        raw = get_reply_text(r)
        cleaned = clean_comment(raw)
        if cleaned:
            all_cleaned_comments.append(cleaned)

    print("Total cleaned comments:", len(all_cleaned_comments))
    # example peek:
    print(all_cleaned_comments[:5])
    
    return all_cleaned_comments

  # for quick local test run