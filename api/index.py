import os, json, base64, secrets, requests
from datetime import datetime, timedelta
from urllib.parse import parse_qs

# Admin config
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
SESSION = {}  # Simple in-memory session for demo (serverless stateless, reset setiap request)

# GitHub config
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "Khisd/Fynexa-key"
FILE_PATH = "keys.json"

API_URL = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github.v3+json"
}

# ---------- Helpers ----------
def load_keys():
    try:
        r = requests.get(API_URL, headers=HEADERS).json()
        content = base64.b64decode(r["content"]).decode()
        return json.loads(content), r["sha"]
    except Exception as e:
        return {}, None

def push_keys(data, sha):
    if not sha: return
    payload = {
        "message": "Update license keys",
        "content": base64.b64encode(json.dumps(data, indent=2).encode()).decode(),
        "sha": sha
    }
    try:
        requests.put(API_URL, headers=HEADERS, json=payload)
    except:
        pass

# ---------- HTML Templates ----------
def render_login(error_msg=""):
    html = f"""
    <html><head><title>Fynexa Login</title></head><body>
    <h2>Login Panel</h2>
    <form method="POST">
        <input type="text" name="user" placeholder="Username" required><br>
        <input type="password" name="pass" placeholder="Password" required><br>
        <button type="submit">Login</button>
    </form>
    <p style='color:red;'>{error_msg}</p>
    </body></html>
    """
    return html

def render_dashboard(keys):
    html = "<html><head><title>Dashboard</title></head><body>"
    html += "<h2>Fynexa Dashboard</h2>"

    # Generate form
    html += """
    <form method="POST">
        <input type="hidden" name="action" value="generate">
        Name: <input type="text" name="name" required>
        Days: <input type="number" name="days" required>
        <button type="submit">Generate Key</button>
    </form><hr>
    """

    # List existing keys with delete
    html += "<ul>"
    for k, info in keys.items():
        html += f"<li>{k} - {info['name']} - {info['status']} - Expire: {info['expire']}"
        html += f"""
        <form method="POST" style="display:inline;">
            <input type="hidden" name="action" value="delete">
            <input type="hidden" name="key" value="{k}">
            <button type="submit">Delete</button>
        </form>
        </li>
        """
    html += "</ul></body></html>"
    return html

# ---------- Vercel handler ----------
def handler(event, context):
    try:
        method = event.get("httpMethod","GET")
        body = event.get("body","")
        params = parse_qs(body)

        # Simple in-memory session by IP (for demo, stateless)
        client_ip = event.get("headers", {}).get("x-forwarded-for", "anon")
        logged_in = SESSION.get(client_ip, False)

        # ---------- Login ----------
        if method=="POST" and not logged_in:
            user = params.get("user", [""])[0]
            pw = params.get("pass", [""])[0]
            if user==ADMIN_USER and pw==ADMIN_PASS:
                SESSION[client_ip]=True
                logged_in = True
            else:
                return {
                    "statusCode": 200,
                    "headers":{"Content-Type":"text/html"},
                    "body": render_login("Invalid credentials")
                }

        # ---------- Dashboard ----------
        if not logged_in:
            return {
                "statusCode": 200,
                "headers":{"Content-Type":"text/html"},
                "body": render_login()
            }

        # Load keys
        keys, sha = load_keys()

        # Handle POST actions
        if method=="POST":
            action = params.get("action", [""])[0]
            if action=="generate":
                key = secrets.token_hex(8)
                days = int(params.get("days", ["1"])[0])
                name = params.get("name", [""])[0]
                keys[key] = {
                    "name": name,
                    "expire": (datetime.now()+timedelta(days=days)).strftime("%Y-%m-%d"),
                    "created": datetime.now().strftime("%Y-%m-%d"),
                    "status": "active"
                }
            elif action=="delete":
                k = params.get("key", [""])[0]
                if k in keys: del keys[k]
            push_keys(keys, sha)

        return {
            "statusCode": 200,
            "headers":{"Content-Type":"text/html"},
            "body": render_dashboard(keys)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"Internal Server Error: {e}"
        }
