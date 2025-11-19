from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from passlib.hash import argon2
from functools import wraps
import re
import time

login_attempts = {} # { ip_address: [timestamps] }
MAX_ATTEMPTS = 5          # number of tries allowed
WINDOW_SECONDS = 60       # time window (1 minute)
LOCKOUT_SECONDS = 120     # temporary lockout after exceeding attempts

DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$abcdefghijklmnopqrstuv$abcdefghijklmnopqrstuvabcdefghijklmnopqrstuv"

# Create the Flask application
app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
)

app.secret_key = "change_this_to_a_random_string"

def check_credentials(username, password):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()

    if row is None:
        # prevent timing attacks by verifying against a dummy hash
        try:
            argon2.verify(password, DUMMY_HASH)
        except:
            pass
        return False
    
    stored_hash = row[0]
    return argon2.verify(password, stored_hash)

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, redirect straight to protected page
    if "user" in session:
        return redirect(url_for("protected"))

    ip = request.remote_addr
    now = time.time()

    # Initialize attempts list if none
    attempts = login_attempts.get(ip, [])

    # Remove attempts older than the window
    attempts = [t for t in attempts if now - t < WINDOW_SECONDS]
    login_attempts[ip] = attempts

    # Check if user is locked out
    if len(attempts) >= MAX_ATTEMPTS:
        return render_template("login.html", 
                               error=f"Too many login attempts. Try again in {LOCKOUT_SECONDS} seconds.")

    if request.method == 'POST':
        # Read form values submitted by the browser
        username = request.form['username']
        username = username.strip()
        if not re.match(r'^[A-Za-z0-9_]{3,30}$', username):
            return render_template("login.html", error="Invalid username format")
        password = request.form['password']
        
        # Validate credentials using check_credentials
        if check_credentials(username, password):
            session["user"] = username
            login_attempts[ip] = []
            return redirect(url_for("protected"))
        else:
            login_attempts[ip].append(now)
            return render_template("login.html", error="Invalid username or password")
    
    # For GET requests, just show the login form
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not re.match("^[A-Za-z0-9_]+$", username):
            return render_template("register.html", error="Invalid username format")

        # Check if the user already exists
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        existing = c.fetchone()

        if existing:
            conn.close()
            return render_template("register.html", error="Username already taken")

        # Hash password
        password_hash = argon2.hash(password)

        # Insert new user
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, password_hash))
        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    # GET request
    return render_template("register.html")

@app.route('/protected')
@login_required
def protected():
    return render_template("protected.html", user=session["user"])
    

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run()
