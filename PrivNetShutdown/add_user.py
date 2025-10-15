# add_user.py. Used to add users to the encrypted SQLite database.
import os, json, base64, tempfile, sqlite3, bcrypt, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type

ENCRYPTED_DB_FILE = "auth.db.enc"
MASTER_PASSPHRASE = os.environ.get("MASTER_PASSPHRASE")

def derive_key(passphrase: bytes, salt: bytes, length=32):
    return hash_secret_raw(
        secret=passphrase, salt=salt, time_cost=2, memory_cost=2**16,
        parallelism=2, hash_len=length, type=Type.ID
    )

def decrypt_db():
    with open(ENCRYPTED_DB_FILE, "r") as f:
        payload = json.load(f)
    salt = base64.b64decode(payload["salt"])
    nonce = base64.b64decode(payload["nonce"])
    ct = base64.b64decode(payload["ct"])
    key = derive_key(MASTER_PASSPHRASE.encode(), salt)
    aes = AESGCM(key)
    plaintext = aes.decrypt(nonce, ct, None)
    return salt, plaintext

def encrypt_db(salt, plaintext):
    key = derive_key(MASTER_PASSPHRASE.encode(), salt)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext, None)
    payload = {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ct": base64.b64encode(ct).decode()
    }
    with open(ENCRYPTED_DB_FILE, "w") as f:
        json.dump(payload, f)

def add_user(username, password):
    salt, decrypted_db_bytes = decrypt_db()

    tf = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db_path = tf.name
    tf.write(decrypted_db_bytes)
    tf.close() # Close the file so sqlite3 can open it

    try:
        conn = sqlite3.connect(temp_db_path)
        c = conn.cursor()
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        c.execute("INSERT OR REPLACE INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
        conn.commit()
        conn.close()

        with open(temp_db_path, "rb") as f:
            updated_db_bytes = f.read()
    finally:
        os.unlink(temp_db_path) # Ensure deletion

    encrypt_db(salt, updated_db_bytes)

if __name__ == "__main__":
    if not MASTER_PASSPHRASE:
        print("ERROR: The MASTER_PASSPHRASE environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    user = input("Username: ").strip()
    if not user:
        print("Username cannot be empty.")
        sys.exit(1)
    pw = input("Password: ").strip()
    if not pw:
        print("Password cannot be empty.")
        sys.exit(1)
    add_user(user, pw)
    print(f"User '{user}' was successfully added or updated.")