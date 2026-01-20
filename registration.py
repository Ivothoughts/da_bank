import sqlite3
import random
import hashlib
import getpass
import re
from datetime import datetime


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_account_number():
    return ''.join(str(random.randint(0, 9)) for _ in range(10))


def register_user():
    conn = sqlite3.connect("bank_database.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("\n--- Welcome to the Registration Window ---")

    # ---------- FIRST NAME ----------
    while True:
        first_name = input("Enter your first name: ").strip().title()

        if not first_name:
            print("❌ First name cannot be empty.")
            continue

        if any(char.isdigit() for char in first_name):
            print("❌ Letters only are allowed in your name.")
            continue

        if len(first_name) < 3 or len(first_name) > 255:
            print("❌ Name must be between 3 and 255 characters.")
            continue

        break

    # ---------- LAST NAME ----------
    while True:
        last_name = input("Enter your last name: ").strip().lower()

        if not last_name:
            print("❌ Last name cannot be empty.")
            continue

        if any(char.isdigit() for char in last_name):
            print("❌ Letters only are allowed in your name.")
            continue

        if len(last_name) < 3 or len(last_name) > 255:
            print("❌ Name must be between 3 and 255 characters.")
            continue

        break

    while True:
        username = input("Enter your username: ").strip().lower()

        # Empty check
        if not username:
            print("❌ Username cannot be empty.")
            continue

        # Identifier check
        if not username.isidentifier():
            print("❌ Only letters, numbers, and underscores are allowed.")
            continue

        # Length check
        if len(username) < 3 or len(username) > 20:
            print("❌ Username must be between 3 and 20 characters.")
            continue

        # Database uniqueness check
        cursor.execute("SELECT 1 FROM customer_info WHERE username = ?", (username,))
        if cursor.fetchone():
            print("❌ Username already exists.")
            continue
        break

    # ---------- PASSWORD ----------
    while True:
        password = getpass.getpass("Enter your password: ").strip()

        if not password:
            print("❌ Password cannot be empty.")
            continue

        if len(password) < 8 or len(password) > 30:
            print("❌ Password must be between 8 and 30 characters.")
            continue

        pwd_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$'
        if not re.match(pwd_pattern, password):
            print("❌ Password must contain uppercase, lowercase, number, and special character.")
            continue

        confirm_password = getpass.getpass("Re-enter your password: ").strip()
        if confirm_password != password:
            print("❌ Passwords do not match.")
            continue

        break

    # ---------- INITIAL DEPOSIT ----------
    while True:
        try:
            initial_deposit = float(input("Enter initial deposit (minimum ₦2000): "))

            if initial_deposit < 2000:
                print("❌ Initial deposit must be at least ₦2000.")
                continue

            break

        except ValueError:
            print("❌ Please enter a valid numeric amount.")

    password_hash = hash_password(password)
    account_number = generate_account_number()

    # ---------- DATABASE INSERT ----------
    try:
        cursor.execute("""
        INSERT INTO customer_info (first_name, last_name, username, password_hash, account_number, balance)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            first_name,
            last_name,
            username,
            password_hash,
            account_number,
            initial_deposit
        ))

        user_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO transactions (user_id, transaction_type, amount)
        VALUES (?, 'deposit', ?)
        """, (user_id, initial_deposit))

        conn.commit()

        print("\n✅ Account created successfully!")
        print(f"🏦 Account Number: {account_number}")

    except sqlite3.IntegrityError:
        print("\n❌ Username already exists. Please choose another.")

    finally:
        conn.close()
