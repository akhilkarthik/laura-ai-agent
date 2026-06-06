import os
import json
import webbrowser
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "openid profile w_member_social"

_auth_code = None


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "code" in params:
            _auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Authorization successful! You can close this tab and return to the terminal.</h2>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h2>Authorization failed. No code received.</h2>")

    def log_message(self, format, *args):
        pass  # suppress server logs


def _get_auth_url(client_id: str) -> str:
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    }
    return f"{LINKEDIN_AUTH_URL}?{urllib.parse.urlencode(params)}"


def _exchange_code(code: str, client_id: str, client_secret: str) -> str:
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = urllib.request.Request(LINKEDIN_TOKEN_URL, data=data)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def _get_person_urn(access_token: str) -> str:
    req = urllib.request.Request("https://api.linkedin.com/v2/userinfo")
    req.add_header("Authorization", f"Bearer {access_token}")
    with urllib.request.urlopen(req) as resp:
        return f"urn:li:person:{json.loads(resp.read())['sub']}"


def run_oauth_flow():
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise ValueError("LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in .env")

    auth_url = _get_auth_url(client_id)
    print(f"\nOpening LinkedIn in your browser...")
    print(f"If it does not open automatically, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    print("Waiting for LinkedIn to redirect back to localhost:8080...")
    HTTPServer(("localhost", 8080), _CallbackHandler).handle_request()

    if not _auth_code:
        raise RuntimeError("Authorization failed — no code received.")

    print("Exchanging code for access token...")
    access_token = _exchange_code(_auth_code, client_id, client_secret)

    print("Fetching your LinkedIn profile URN...")
    person_urn = _get_person_urn(access_token)

    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    with open(env_path, "a") as f:
        f.write(f"\nLINKEDIN_ACCESS_TOKEN={access_token}\n")
        f.write(f"LINKEDIN_PERSON_URN={person_urn}\n")

    print(f"\nDone! Token and URN saved to .env")
    print(f"Person URN: {person_urn}")
