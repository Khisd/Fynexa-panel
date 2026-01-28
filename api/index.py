from flask import Flask, render_template, request, redirect, session
import os, json, base64, secrets, requests, serverless_wsgi
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "fynexa-secret"

ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO = "Khisd/Fynexa-key"
FILE_PATH = "keys.json"

API_URL = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Helpers load / push keys
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

# Routes
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        if request.form["user"]==ADMIN_USER and request.form["pass"]==ADMIN_PASS:
            session["login"]=True
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if not session.get("login"):
        return redirect("/")
    keys, sha = load_keys()
    if request.method=="POST":
        action = request.form["action"]
        if action=="generate":
            key = secrets.token_hex(8)
            days = int(request.form["days"])
            name = request.form["name"]
            keys[key] = {
                "name": name,
                "expire": (datetime.now()+timedelta(days=days)).strftime("%Y-%m-%d"),
                "created": datetime.now().strftime("%Y-%m-%d"),
                "status": "active"
            }
        elif action=="delete":
            k = request.form["key"]
            if k in keys: del keys[k]
        push_keys(keys, sha)
        return redirect("/dashboard")
    return render_template("dashboard.html", keys=keys)

# Vercel handler
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)

# Local testing
if __name__=="__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
