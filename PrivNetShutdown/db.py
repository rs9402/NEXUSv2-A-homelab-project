# encrypt_db.py
# creates the encrypted database file auth.db.enc which interfaces with auth.py for authentication
# requires the MASTER_PASSPHRASE environment variable. Set in env by startup ps script.
import sqlite3, os, json, sys, tempfile
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type
import bcrypt
import base64

ENCRYPTED = "auth.db.enc"
MASTER_PASSPHRASE = os.environ.get("MASTER_PASSPHRASE")

def derive_key(passphrase: bytes, salt: bytes, length=32):
    return hash_secret_raw(
        secret=passphrase, salt=salt, time_cost=2, memory_cost=2**16,
        parallelism=2, hash_len=length, type=Type.ID
    )

def create_and_get_db_bytes():
    """Securely creates a new SQLite database and returns its byte representation."""
    # Create a temporary file but don't auto-delete it yet.
    tf = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    temp_db_path = tf.name
    # Close the file handle immediately so sqlite3 can open it.
    tf.close()

    try:
        # Connect to the database using its path.
        conn = sqlite3.connect(temp_db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE users (username TEXT PRIMARY KEY, password_hash TEXT NOT NULL)")
        pw = "Darkminez1!".encode()
        pw_hash = bcrypt.hashpw(pw, bcrypt.gensalt()).decode()
        c.execute("INSERT INTO users VALUES (?, ?)", ("Admin", pw_hash))
        conn.commit()
        conn.close()

        # Re-open the file in binary mode to read its contents.
        with open(temp_db_path, "rb") as f:
            db_bytes = f.read()
    finally:
        # Securely delete the temporary file, even if errors occurred.
        os.unlink(temp_db_path)
        
    return db_bytes

def encrypt_db(db_bytes):
    salt = os.urandom(16)
    key = derive_key(MASTER_PASSPHRASE.encode(), salt)
    aes = AESGCM(key)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, db_bytes, None)
    payload = {
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ct": base64.b64encode(ct).decode()
    }
    with open(ENCRYPTED, "w") as f:
        json.dump(payload, f)
    print(f"Encrypted database created successfully at '{ENCRYPTED}'")

if __name__ == "__main__":
    if not MASTER_PASSPHRASE:
        print("ERROR: The MASTER_PASSPHRASE environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    database_bytes = create_and_get_db_bytes()
    encrypt_db(database_bytes)