from flask import Flask, render_template, request, redirect, url_for, session


# Create the Flask application
app = Flask(__name__)

# Secret key used to sign session cookies.
# In production, load this from an environment variable or a secrets manager.
app.secret_key = "seupersecretkey"

# Hard-coded credentials for demonstration. Replace with a proper user store
# (database + hashed passwords) for anything beyond examples or testing.
USERNAME = "testuser"
PASSWORD = "password123"


@app.route('/')
def index():
    """Render the public landing page.

    Returns the `index.html` template which contains a link to the login page.
    """
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login form display and submission.

    - GET requests: render the login form.
    - POST requests: validate credentials and set `session['user']` on success.
      On successful login the user is redirected to the protected page.

    Note: This uses plain-text comparison for demonstration. Real apps must
    compare hashed passwords and implement rate-limiting, account lockouts,
    and CSRF protection.
    """
    if request.method == 'POST':
        # Read form values submitted by the browser
        username = request.form['username']
        password = request.form['password']
        
        # Simple validation: compare against the demo credentials
        if username == USERNAME and password == PASSWORD:
            # Store the username in the session to mark the user as authenticated
            session["user"] = username
            # Redirect to the protected page once authenticated
            return redirect(url_for("protected"))
        else:
            # Render the login template again with an error message
            return render_template('login.html', error="Invalid credentials")
    
    # For GET requests, just show the login form
    return render_template("login.html")


@app.route('/protected')
def protected():
    """Render a protected page only accessible to logged-in users.

    The route checks for the presence of `session['user']`. If present,
    it renders `protected.html` and passes the username into the template.
    Otherwise the client is redirected to the login page.
    """
    if "user" in session:
        # session['user'] is considered the authenticated identity here
        return render_template("protected.html", user=session["user"])
    else:
        # Not authenticated: send user to login
        return redirect(url_for("login"))
    

@app.route('/logout')
def logout():
    """Log the user out by removing their identity from the session.

    session.pop("user", None) removes the 'user' key if it exists and has no
    effect otherwise. This effectively signs the user out.
    """
    session.pop("user", None)
    return redirect(url_for("index"))


if __name__ == '__main__':
    # Default development server. For production use a WSGI server like
    # Gunicorn/Uvicorn and ensure debug is disabled.
    app.run()
