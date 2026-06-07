import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
load_dotenv()

import json
import urllib.request
from db.schedule_store import get_due_posts, mark_posted
from linkedin.poster import post_to_linkedin


def notify(user_id: int, text: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    payload = json.dumps({"chat_id": user_id, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=payload, method="POST"
    )
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req):
        pass


def run():
    try:
        due, all_posts, sha = get_due_posts()
    except Exception as e:
        print(f"Error reading scheduled posts: {e}")
        return

    if not due:
        print("No posts due.")
        return

    for item in due:
        print(f"Posting scheduled item {item['id']}...")
        try:
            post_id, post_url = post_to_linkedin(item["post"])
            mark_posted(all_posts, sha, item["id"])
            print(f"Posted: {post_id}")
            try:
                notify(item["user_id"], f"Your scheduled post is live!\n\n{post_url}\n\nWhen you check the stats, tell me the numbers and I'll track them.")
            except Exception as e:
                print(f"Notification failed: {e}")
        except Exception as e:
            print(f"Failed to post {item['id']}: {e}")
            try:
                notify(item["user_id"], f"Failed to post your scheduled LinkedIn post: {e}")
            except:
                pass


if __name__ == "__main__":
    run()
