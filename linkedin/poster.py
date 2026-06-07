import os
import json
import urllib.request
import urllib.error

POSTS_URL = "https://api.linkedin.com/v2/ugcPosts"


def post_to_linkedin(text: str) -> str:
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    person_urn = os.getenv("LINKEDIN_PERSON_URN")

    if not access_token or not person_urn:
        raise ValueError("LinkedIn not set up. Run setup_linkedin.py first.")

    payload = json.dumps({
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }).encode()

    req = urllib.request.Request(POSTS_URL, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {access_token}")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-Restli-Protocol-Version", "2.0.0")

    try:
        with urllib.request.urlopen(req) as resp:
            post_id = resp.headers.get("x-restli-id", "unknown")
            post_url = f"https://www.linkedin.com/feed/update/{post_id}"
            return post_id, post_url
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"LinkedIn API error {e.code}: {body}")
