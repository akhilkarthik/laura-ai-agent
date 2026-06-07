import os
import json
import urllib.request


def send_email(to: str, subject: str, body: str):
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise ValueError("RESEND_API_KEY not set")

    payload = json.dumps({
        "from": "Laura <onboarding@resend.dev>",
        "to": [to],
        "subject": subject,
        "text": body
    }).encode()

    req = urllib.request.Request("https://api.resend.com/emails", data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())
