import os
import json
import urllib.request
from datetime import datetime, timezone, timedelta

NOTION_VERSION = "2022-06-28"
API_BASE = "https://api.notion.com/v1"
IST = timezone(timedelta(hours=5, minutes=30))


def _headers():
    token = os.getenv("NOTION_API_KEY")
    if not token:
        raise ValueError("NOTION_API_KEY not set")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION,
    }


def create_page(title: str, content: str) -> str:
    parent_id = os.getenv("NOTION_PAGE_ID", "378420a3ea01812fafc8e1d10d5f6b67")
    now = datetime.now(IST).strftime("%d %b %Y %I:%M %p IST")

    blocks = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": f"Saved: {now}"}, "annotations": {"color": "gray"}}]
            }
        },
        {"object": "block", "type": "divider", "divider": {}}
    ]

    for para in content.split('\n'):
        if para.strip():
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": para}}]
                }
            })

    payload = json.dumps({
        "parent": {"page_id": parent_id},
        "properties": {
            "title": {"title": [{"text": {"content": title}}]}
        },
        "children": blocks
    }).encode()

    req = urllib.request.Request(f"{API_BASE}/pages", data=payload, method="POST")
    for k, v in _headers().items():
        req.add_header(k, v)

    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
        return data.get("url", "")
