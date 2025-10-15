# auth_service.py. Microservice running locally to verify user credentials.
# Expects an encrypted SQLite database file 'auth.db.enc' with a 'users' table
import os, json, sqlite3, base64, time, sys, tempfile
from flask import Flask, request, jsonify, abort
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import bcrypt

ENCRYPTED = "auth.db.enc"
MASTER_PASSPHRASE = os.environ.get("MASTER_PASSPHRASE") # Set in env by powershell script
AUTH_SHARED_SECRET = os.environ.get("AUTH_SHARED_SECRET") # Set in env by powershell script

app = Flask(__name__)
nonce_cache = {}

def derive_key(passphrase: bytes, salt: bytes, length=32):
    return hash_secret_raw(
        secret=passphrase, salt=salt, time_cost=2, memory_cost=2**16,
        parallelism=2, hash_len=length, type=Type.ID
    )

def get_user_hash_from_db(db_bytes, username):
    """Writes db bytes to a secure temp file to query, then auto-deletes."""
    tf = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db_path = tf.name
    tf.write(db_bytes)
    tf.close() # Close file handle so sqlite3 can open it.

    try:
        conn = sqlite3.connect(temp_db_path)
        c = conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        row = c.fetchone()
        conn.close()
    finally:
        os.unlink(temp_db_path) # Ensure deletion

    return row[0] if row else None

@app.route("/verify", methods=["POST"])
def verify():
    if request.headers.get("X-SHARED-SECRET") != AUTH_SHARED_SECRET:
        abort(403)
    data = request.get_json()
    if not all(k in data for k in ["username", "password", "timestamp", "nonce"]):
        return jsonify({"ok": False, "error": "missing required fields"}), 400
    username, password, ts, nonce = data["username"], data["password"], float(data["timestamp"]), data["nonce"]

    current_time = time.time()
    if abs(current_time - ts) > 30:
        return jsonify({"ok": False, "error": "stale timestamp"}), 400
    for n, timestamp in list(nonce_cache.items()):
        if current_time - timestamp > 60:
            del nonce_cache[n]
    if nonce in nonce_cache:
        return jsonify({"ok": False, "error": "replay attack detected"}), 400
    nonce_cache[nonce] = current_time

    try:
        with open(ENCRYPTED, "r") as f:
            payload = json.load(f)
        salt = base64.b64decode(payload["salt"])
        key = derive_key(MASTER_PASSPHRASE.encode(), salt)
        aes = AESGCM(key)
        db_bytes = aes.decrypt(base64.b64decode(payload["nonce"]), base64.b64decode(payload["ct"]), None)
        stored_hash = get_user_hash_from_db(db_bytes, username)
    except FileNotFoundError:
        print(f"ERROR: Encrypted database '{ENCRYPTED}' not found.", file=sys.stderr)
        return jsonify({"ok": False, "error": "server configuration error"}), 500
    except Exception as e:
        print(f"ERROR: A database decryption or query error occurred: {e}", file=sys.stderr)
        return jsonify({"ok": False, "error": "invalid credentials or server error"}), 500

    if not stored_hash:
        return jsonify({"ok": False, "error": "user not found"}), 404
    if bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return jsonify({"ok": True})
    else:
        return jsonify({"ok": False, "error": "invalid credentials"}), 403

if __name__ == "__main__":
    if not MASTER_PASSPHRASE or not AUTH_SHARED_SECRET:
        print("ERROR: Set MASTER_PASSPHRASE and AUTH_SHARED_SECRET in your environment.", file=sys.stderr)
        sys.exit(1)
    app.run(host="127.0.0.1", port=5001)