from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "seupersecretkey"

#hardcoded user credentials
USERNAME = "testuser"
PASSWORD = "password123"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == USERNAME and password == PASSWORD:
            session["user"] = username
            return redirect(url_for("protected"))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template("login.html")

@app.route('/protected')
def protected():
    if "user" in session:
        return render_template("protected.html", user=session["user"])
    else:
        return redirect(url_for("login"))
    
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run()