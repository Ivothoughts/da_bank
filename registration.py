import sqlite3
import random
import hashlib
import getpass
import re


DB_FILE = "bank_database.db"


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def generate_unique_account_number(cursor):
    while True:
        acc = ''.join(str(random.randint(0, 9)) for _ in range(10))
        cursor.execute(
            "SELECT 1 FROM customer_info WHERE account_number = ?",
            (acc,)
        )
        if not cursor.fetchone():
            return acc


def register_user():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    print("\n--- Welcome to the Registration Window ---")

    # ---------- FIRST NAME ----------
    while True:
        first_name = input("Enter your first name: ").strip().title()
        if not first_name or any(char.isdigit() for char in first_name):
            print("❌ Letters only. Field cannot be empty.")
            continue
        if not 3 <= len(first_name) <= 255:
            print("❌ Name must be between 3 and 255 characters.")
            continue
        break

    # ---------- LAST NAME ----------
    while True:
        last_name = input("Enter your last name: ").strip().title()
        if not last_name or any(char.isdigit() for char in last_name):
            print("❌ Letters only. Field cannot be empty.")
            continue
        if not 3 <= len(last_name) <= 255:
            print("❌ Name must be between 3 and 255 characters.")
            continue
        break

    # ---------- USERNAME ----------
    while True:
        username = input("Enter your username: ").strip().lower()

        if not username:
            print("❌ Username cannot be empty.")
            continue
        if not username.isidentifier():
            print("❌ Only letters, numbers, and underscores allowed.")
            continue
        if not 3 <= len(username) <= 20:
            print("❌ Username must be between 3 and 20 characters.")
            continue

        cursor.execute(
            "SELECT 1 FROM customer_info WHERE username = ?",
            (username,)
        )
        if cursor.fetchone():
            print("❌ Username already exists.")
            continue

        break

    # ---------- PASSWORD ----------
    while True:
        password = getpass.getpass("Enter your password: ").strip()

        if not 8 <= len(password) <= 30:
            print("❌ Password must be between 8 and 30 characters.")
            continue

        if not re.match(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).+$',
            password
        ):
            print("❌ Must contain upper, lower, number & special character.")
            continue

        confirm = getpass.getpass("Re-enter your password: ").strip()
        if password != confirm:
            print("❌ Passwords do not match.")
            continue

        break

    # ---------- INITIAL DEPOSIT ----------
    while True:
        try:
            initial_deposit = float(input("Enter initial deposit (minimum ₦2000): "))
            if initial_deposit < 2000:
                print("❌ Minimum deposit is ₦2000.")
                continue
            break
        except ValueError:
            print("❌ Enter a valid amount.")

    password_hash = hash_password(password)
    account_number = generate_unique_account_number(cursor)

    # ---------- DATABASE INSERT ----------
    try:
        cursor.execute("""
            INSERT INTO customer_info (
                first_name,
                last_name,
                username,
                password_hash,
                account_number,
                balance
            )
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
            VALUES (?, 'Deposit', ?)
        """, (user_id, initial_deposit))

        conn.commit()

        print("\n✅ Account created successfully!")
        print(f"🏦 Account Number: {account_number}")

    except sqlite3.IntegrityError as e:
        print("❌ Registration failed:", e)

    finally:
        conn.close()
