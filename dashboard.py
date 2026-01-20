import sqlite3
import hashlib
import re
import time
from getpass import getpass

DB_FILE = "bank_database.db"

MAX_USERNAME_ATTEMPTS = 3
MAX_PASSWORD_ATTEMPTS = 3


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def login_user():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("\n--- Login to Iffy's Money Bank ---")
    print("Your money is our lifeline. Fret not, for we guard it with unwavering dedication.")

    # ================= USERNAME AUTH =================
    username_attempts = 0
    user = None

    while username_attempts < MAX_USERNAME_ATTEMPTS:
        username = input("Enter your username (or 0 to cancel): ").strip().lower()

        if username == "0":
            print("Login cancelled.")
            conn.close()
            return None

        if not re.fullmatch(r"[a-z0-9_]+", username):
            print("❌ Invalid username format.")
            continue

        cursor.execute("""
            SELECT 
                id,
                first_name,
                last_name,
                username,
                account_number,
                balance,
                password_hash
            FROM customer_info
            WHERE username = ?
        """, (username,))

        user = cursor.fetchone()

        if not user:
            username_attempts += 1
            remaining = MAX_USERNAME_ATTEMPTS - username_attempts
            print(f"❌ Username not found. Attempts left: {remaining}")
            continue

        break  # username is valid

    if not user:
        print("🚫 Too many invalid username attempts. Please try again later.")
        conn.close()
        return None

    # ================= PASSWORD AUTH =================
    password_attempts = 0
    stored_password_hash = user[6]

    while password_attempts < MAX_PASSWORD_ATTEMPTS:
        password = getpass("Enter your password: ").strip()

        if len(password) < 8 or len(password) > 30:
            print("❌ Password length must be between 8 and 30 characters.")
            continue

        hashed_password = hash_password(password)

        if hashed_password != stored_password_hash:
            password_attempts += 1
            remaining = MAX_PASSWORD_ATTEMPTS - password_attempts
            print(f"❌ Incorrect password. Attempts left: {remaining}")
            continue

        # ================= SUCCESS =================
        print("\nLogging in...")
        time.sleep(2)
        print("✅ Login successful!")
        print(f"🏦 Welcome back, {user[1].title()} {user[2].title()}")

        conn.close()
        return user[:6]  # exclude password hash

    print("🚫 Too many failed password attempts. Account temporarily locked.")
    conn.close()
    return None
