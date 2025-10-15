# webui.py. Gives a simple webui for shutting down the server.
# Requires an auth service running on localhost:5001
from flask import Flask, render_template_string, request, redirect, url_for, session, abort
import os, time, secrets, requests, sys

app = Flask(__name__)
# IMPORTANT: Set a fixed, secret key in your environment for production
app.secret_key = os.environ.get("FLASK_SESSION_KEY", secrets.token_hex(32))

AUTH_SERVICE_URL = "http://127.0.0.1:5001/verify"
AUTH_SHARED_SECRET = os.environ.get("AUTH_SHARED_SECRET")

# --- Page Templates ---

login_page = """
<!DOCTYPE html>
<html>
<head><title>Login</title>
<style>
    body {
        font-family: monospace;
    }
    .question-mark {
        position: fixed;
        bottom: 20px;
        right: 20px;
        font-size: 2em;
        cursor: pointer;
        text-decoration: none;
        color: #000;
        opacity: 0.5;
        transition: opacity 0.3s;
    }
    .question-mark:hover {
        opacity: 1;
    }
</style>
</head>
<body>
  <h2>Login to Server Control</h2>
  {% if error %}
    <p style="color:red;">{{ error }}</p>
  {% endif %}
  <form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <input name="username" placeholder="Username" required><br>
    <input name="password" type="password" placeholder="Password" required><br><br>
    <button type="submit">Login</button>
  </form>
  <a href="{{ url_for('easter_egg') }}" class="question-mark">?</a>
</body>
</html>
"""

control_page = """
<!DOCTYPE html>
<html>
<head><title>Control Panel</title></head>
<body>
  <h2>Welcome, {{ session['user'] }}!</h2>
  <p>From here you can perform system actions.</p>
  <a href="{{ url_for('shutdown_confirm') }}" style="background-color: #f44336; color: white; padding: 10px; text-decoration: none; border-radius: 5px;">Shutdown Server</a>
  <br>
  <br>
  <a href="{{ url_for('logout') }}">Logout</a>
</body>
</html>
"""

shutdown_confirm_page = """
<!DOCTYPE html>
<html>
<head><title>Confirm Shutdown</title></head>
<body>
  <h2>Confirm Server Shutdown</h2>
  <p style="color:red; font-weight: bold;">This action is irreversible. Please re-enter your password to proceed.</p>
  {% if error %}
    <p style="color:red;">{{ error }}</p>
  {% endif %}
  <form method="POST" action="{{ url_for('shutdown_action') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <input name="password" type="password" placeholder="Password" required><br><br>
    <button type="submit">CONFIRM SHUTDOWN</button>
  </form>
  <br>
  <a href="{{ url_for('control') }}">Cancel</a>
</body>
</html>
"""

easter_egg_page = """
<!DOCTYPE html>
<html>
<head><title>???</title>
<style>
    body {
        background-color: #000;
        color: #0f0;
        font-family: monospace;
        white-space: pre;
    }
</style>
</head>
<body>
<pre>
Brought to you by...

EASTER EGG REDACTED FOR MY PRIVACY
                                                                                                
</pre>
<a href="{{ url_for('login') }}">Go back</a>
</body>
</html>
"""

# --- CSRF Protection ---

@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('csrf_token'):
            abort(403) # Forbidden

def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

# --- Helper Functions ---

def call_auth_service(username, password):
    """Calls the auth service to verify credentials."""
    payload = {
        "username": username,
        "password": password,
        "timestamp": str(time.time()),
        "nonce": secrets.token_hex(8)
    }
    headers = {"X-SHARED-SECRET": AUTH_SHARED_SECRET}
    try:
        r = requests.post(AUTH_SERVICE_URL, json=payload, headers=headers, timeout=3)
        return r
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Auth service unreachable: {e}", file=sys.stderr)
        return None

def shutdown_system():
    """Executes the system shutdown command based on the OS."""
    print("SHUTDOWN INITIATED...")
    system = sys.platform
    if system == "win32":
        os.system("shutdown /s /t 1")
    else: # For Linux and macOS
        os.system("shutdown now")
    # Add this line to exit the application after the command is issued
    os._exit(0)

# --- Routes ---

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        response = call_auth_service(username, password)
        
        if response and response.status_code == 200:
            session.clear()
            session["user"] = username
            return redirect(url_for("control"))
        else:
            error_msg = "Login failed. Please check your credentials."
            if response is not None and response.json():
                print(f"Auth failed with message: {response.json().get('error')}")
            return render_template_string(login_page, error=error_msg)
            
    return render_template_string(login_page, error=None)

@app.route("/control")
def control():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string(control_page)

@app.route("/shutdown_confirm")
def shutdown_confirm():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string(shutdown_confirm_page)

@app.route("/shutdown", methods=["POST"])
def shutdown_action():
    if "user" not in session:
        return redirect(url_for("login"))
    
    password = request.form.get("password")
    if not password:
        return render_template_string(shutdown_confirm_page, error="Password is required.")
        
    username = session["user"]
    
    response = call_auth_service(username, password)

    if response and response.status_code == 200:
        shutdown_system()
        return "Server is shutting down now."
    else:
        return render_template_string(shutdown_confirm_page, error="Incorrect password.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
    
@app.route('/easter-egg')
def easter_egg():
    return render_template_string(easter_egg_page)

if __name__ == "__main__":
    if not AUTH_SHARED_SECRET or not os.environ.get("FLASK_SESSION_KEY"):
        print("ERROR: Set AUTH_SHARED_SECRET and FLASK_SESSION_KEY in your environment.", file=sys.stderr)
        sys.exit(1)
    
    app.run(host="0.0.0.0", port=1234)