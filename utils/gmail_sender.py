import os
import json
import base64
import urllib.request


def send_email(to: str, subject: str, body: str):
    api_key = os.getenv("MAILJET_API_KEY")
    secret_key = os.getenv("MAILJET_SECRET_KEY")
    from_email = os.getenv("MAILJET_FROM_EMAIL", "akhilkarthik0007@gmail.com")

    if not api_key or not secret_key:
        raise ValueError("MAILJET_API_KEY and MAILJET_SECRET_KEY not set")

    credentials = base64.b64encode(f"{api_key}:{secret_key}".encode()).decode()

    payload = json.dumps({
        "Messages": [{
            "From": {"Email": from_email, "Name": "Laura"},
            "To": [{"Email": to}],
            "Subject": subject,
            "TextPart": body
        }]
    }).encode()

    req = urllib.request.Request("https://api.mailjet.com/v3.1/send", data=payload, method="POST")
    req.add_header("Authorization", f"Basic {credentials}")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())
