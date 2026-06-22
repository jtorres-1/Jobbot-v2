from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import os
import stripe
import hashlib
import secrets
from scraper import scrape_jobs
from resume_parser import parse_resume
from applier import apply_to_job
import threading

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "changeme")
CORS(app, supports_credentials=True)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PRICE_ID = os.environ.get("STRIPE_PRICE_ID")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

DB = "jobbot.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        stripe_customer_id TEXT,
        stripe_subscription_id TEXT,
        subscribed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        keywords TEXT,
        location TEXT,
        remote INTEGER DEFAULT 0,
        companies TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        job_title TEXT,
        company TEXT,
        job_url TEXT,
        status TEXT,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(email):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()
    return user

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = hash_password(data.get("password"))
    try:
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except:
        return jsonify({"error": "Email already exists"}), 400

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = hash_password(data.get("password"))
    user = get_user(email)
    if user and user[2] == password:
        session["user_id"] = user[0]
        session["email"] = email
        return jsonify({"success": True, "subscribed": user[5]})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route("/api/subscribe", methods=["POST"])
def subscribe():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.json
    token = data.get("token")
    email = session["email"]
    try:
        customer = stripe.Customer.create(email=email, source=token)
        subscription = stripe.Subscription.create(
            customer=customer.id,
            items=[{"price": STRIPE_PRICE_ID}]
        )
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("UPDATE users SET stripe_customer_id=?, stripe_subscription_id=?, subscribed=1 WHERE id=?",
                  (customer.id, subscription.id, session["user_id"]))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/preferences", methods=["POST"])
def save_preferences():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    data = request.json
    keywords = ",".join(data.get("keywords", []))
    location = data.get("location", "")
    remote = 1 if data.get("remote") else 0
    companies = ",".join(data.get("companies", []))
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM preferences WHERE user_id=?", (session["user_id"],))
    c.execute("INSERT INTO preferences (user_id, keywords, location, remote, companies) VALUES (?, ?, ?, ?, ?)",
              (session["user_id"], keywords, location, remote, companies))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/preferences", methods=["GET"])
def get_preferences():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM preferences WHERE user_id=?", (session["user_id"],))
    pref = c.fetchone()
    conn.close()
    if not pref:
        return jsonify({})
    return jsonify({
        "keywords": pref[2].split(",") if pref[2] else [],
        "location": pref[3],
        "remote": bool(pref[4]),
        "companies": pref[5].split(",") if pref[5] else []
    })

@app.route("/api/upload-resume", methods=["POST"])
def upload_resume():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    file = request.files.get("resume")
    if not file:
        return jsonify({"error": "No file"}), 400
    path = f"resumes/{session['user_id']}.pdf"
    os.makedirs("resumes", exist_ok=True)
    file.save(path)
    return jsonify({"success": True})

@app.route("/api/run", methods=["POST"])
def run_bot():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    user = get_user(session["email"])
    if not user[5]:
        return jsonify({"error": "Subscription required"}), 403

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM preferences WHERE user_id=?", (session["user_id"],))
    pref = c.fetchone()
    conn.close()

    if not pref:
        return jsonify({"error": "Set preferences first"}), 400

    keywords = pref[2].split(",") if pref[2] else []
    location = pref[3]
    remote = bool(pref[4])
    companies = pref[5].split(",") if pref[5] else []
    resume_path = f"resumes/{session['user_id']}.pdf"

    if not os.path.exists(resume_path):
        return jsonify({"error": "Upload resume first"}), 400

    def run():
        resume_data = parse_resume(resume_path)
        jobs = scrape_jobs(keywords, location, remote, companies)
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        for job in jobs:
            result = apply_to_job(job, resume_data)
            c.execute("INSERT INTO applications (user_id, job_title, company, job_url, status) VALUES (?, ?, ?, ?, ?)",
                      (session["user_id"], job["title"], job["company"], job["url"], result["status"]))
        conn.commit()
        conn.close()

    threading.Thread(target=run).start()
    return jsonify({"success": True, "message": "Bot is running"})

@app.route("/api/applications", methods=["GET"])
def get_applications():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT job_title, company, job_url, status, applied_at FROM applications WHERE user_id=? ORDER BY applied_at DESC",
              (session["user_id"],))
    apps = c.fetchall()
    conn.close()
    return jsonify([{"title": a[0], "company": a[1], "url": a[2], "status": a[3], "date": a[4]} for a in apps])

@app.route("/api/webhook", methods=["POST"])
def webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, os.environ.get("STRIPE_WEBHOOK_SECRET"))
        if event["type"] == "customer.subscription.deleted":
            customer_id = event["data"]["object"]["customer"]
            conn = sqlite3.connect(DB)
            c = conn.cursor()
            c.execute("UPDATE users SET subscribed=0 WHERE stripe_customer_id=?", (customer_id,))
            conn.commit()
            conn.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5003)
