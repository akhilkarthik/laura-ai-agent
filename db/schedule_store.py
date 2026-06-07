import os
import json
import uuid
import base64
import urllib.request
import urllib.error
from datetime import datetime, timezone


def _headers():
    return {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github.v3+json",
    }


def _repo():
    return os.getenv("GITHUB_REPO", "akhilkarthik/linkedin-telegram-agent")


def _get_file():
    url = f"https://api.github.com/repos/{_repo()}/contents/data/scheduled_posts.json"
    req = urllib.request.Request(url, headers=_headers())
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    content = json.loads(base64.b64decode(data["content"]).decode())
    return content, data["sha"]


def _put_file(content, sha, message):
    url = f"https://api.github.com/repos/{_repo()}/contents/data/scheduled_posts.json"
    payload = json.dumps({
        "message": message,
        "content": base64.b64encode(json.dumps(content, indent=2).encode()).decode(),
        "sha": sha,
    }).encode()
    req = urllib.request.Request(url, data=payload, method="PUT", headers=_headers())
    with urllib.request.urlopen(req):
        pass


def add_post(user_id: int, post: str, scheduled_at: str) -> str:
    posts, sha = _get_file()
    post_id = str(uuid.uuid4())[:8]
    posts.append({
        "id": post_id,
        "user_id": user_id,
        "post": post,
        "scheduled_at": scheduled_at,
        "posted": False,
    })
    _put_file(posts, sha, f"schedule post {post_id}")
    return post_id


def get_due_posts():
    posts, sha = _get_file()
    now = datetime.now(timezone.utc)
    due = [p for p in posts if not p["posted"] and datetime.fromisoformat(p["scheduled_at"]) <= now]
    return due, posts, sha


def mark_posted(posts, sha, post_id):
    for p in posts:
        if p["id"] == post_id:
            p["posted"] = True
    _put_file(posts, sha, f"mark posted {post_id}")


def get_pending(user_id: int = None):
    posts, _ = _get_file()
    pending = [p for p in posts if not p["posted"]]
    if user_id:
        pending = [p for p in pending if p["user_id"] == user_id]
    return pending


def cancel_post(user_id: int, post_id: str) -> bool:
    posts, sha = _get_file()
    for p in posts:
        if p["id"] == post_id and p["user_id"] == user_id and not p["posted"]:
            p["posted"] = True
            _put_file(posts, sha, f"cancel post {post_id}")
            return True
    return False
