from flask import Flask, render_template, request, redirect, session
import os, json, base64, secrets, requests
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "fynexa-secret"

# ===== ENV (SET DI VERCEL) =====
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "admin123")

REPO = "Khisd/Fynexa-key"
FILE_PATH = "keys.json"

API_URL = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ===== HELPERS =====
def load_keys():
    r = requests.get(API_URL, headers=HEADERS).json()
    content = base64.b64decode(r["content"]).decode()
    return json.loads(content), r["sha"]

def push_keys(data, sha):
    payload = {
        "message": "Update license keys",
        "content": base64.b64encode(json.dumps(data, indent=2).encode()).decode(),
        "sha": sha
    }
    requests.put(API_URL, headers=HEADERS, json=payload)

# ===== ROUTES =====
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["user"] == ADMIN_USER and request.form["pass"] == ADMIN_PASS:
            session["login"] = True
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not session.get("login"):
        return redirect("/")

    keys, sha = load_keys()

    if request.method == "POST":
        action = request.form["action"]

        if action == "generate":
            key = secrets.token_hex(8)
            days = int(request.form["days"])
            name = request.form["name"]

            keys[key] = {
                "name": name,
                "expire": (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d"),
                "created": datetime.now().strftime("%Y-%m-%d"),
                "status": "active"
            }

        elif action == "delete":
            k = request.form["key"]
            if k in keys:
                del keys[k]

        push_keys(keys, sha)
        return redirect("/dashboard")

    return render_template("dashboard.html", keys=keys)

# ===== VERCEL ENTRY =====
def handler(environ, start_response):
    return app(environ, start_response)
