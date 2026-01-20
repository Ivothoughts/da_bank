import sqlite3
import time
import color
from datetime import datetime

DB_FILE = "bank_database.db"


def dashboard(user):
    """
    user tuple format:
    (id, first_name, last_name, username, account_number, balance)
    """
    user_id, first_name, last_name, username, account_number, balance = user

    print(f"\nWelcome {first_name.title()} {last_name.title()} 👋")
    time.sleep(1)

    while True:
        print("""
------------------ DASHBOARD ------------------
1. Deposit
2. Withdraw
3. Check Balance
4. Transaction History
5. Transfer
6. Logout
----------------------------------------------
""")

        choice = input("Select an option (1-6): ").strip()

        if choice == "1":
            deposit(user_id)
        elif choice == "2":
            withdraw(user_id)
        elif choice == "3":
            check_balance(user_id)
        elif choice == "4":
            transaction_history(user_id)
        elif choice == "5":
            transfer(user_id, account_number)
        elif choice == "6":
            print("Logging out...")
            time.sleep(1)
            print("✅ Logged out successfully.\n")
            break
        else:
            print("❌ Invalid selection. Try again.")

def deposit(user_id):
    while True:
        try:
            amount = float(input("Enter deposit amount: ₦"))

            if amount <= 0:
                print("❌ Deposit amount must be greater than zero.")
                continue

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT balance FROM customer_info WHERE id = ?",
                    (user_id,)
                )
                current_balance = cursor.fetchone()[0]

                new_balance = current_balance + amount

                cursor.execute(
                    "UPDATE customer_info SET balance = ? WHERE id = ?",
                    (new_balance, user_id)
                )

                cursor.execute("""
                    INSERT INTO transactions (user_id, type, amount)
                    VALUES (?, 'deposit', ?)
                """, (user_id, amount))

                conn.commit()

            print("Processing deposit...")
            time.sleep(2)
            print(f"✅ Deposit successful. New balance: ₦{new_balance:.2f}")
            break

        except ValueError:
            print("❌ Enter a valid amount.")

def withdraw(user_id):
    while True:
        try:
            amount = float(input("Enter withdrawal amount: ₦"))

            if amount <= 0:
                print("❌ Withdrawal amount must be greater than zero.")
                continue

            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT balance FROM customer_info WHERE id = ?",
                    (user_id,)
                )
                current_balance = cursor.fetchone()[0]

                if amount > current_balance:
                    print("❌ Insufficient balance.")
                    continue

                new_balance = current_balance - amount

                cursor.execute(
                    "UPDATE customer_info SET balance = ? WHERE id = ?",
                    (new_balance, user_id)
                )

                cursor.execute("""
                    INSERT INTO transactions (user_id, type, amount)
                    VALUES (?, 'withdrawal', ?)
                """, (user_id, amount))

                conn.commit()

            print("Processing withdrawal...")
            time.sleep(2)
            print(f"✅ Withdrawal successful. New balance: ₦{new_balance:.2f}")
            break

        except ValueError:
            print("❌ Enter a valid amount.")

def check_balance(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT balance FROM customer_info WHERE id = ?",
            (user_id,)
        )
        balance = cursor.fetchone()[0]

    print("Fetching balance...")
    time.sleep(1)
    print(f"💰 Current balance: ₦{balance:.2f}")

def transaction_history(user_id):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT type, amount, timestamp
            FROM transactions
            WHERE user_id = ?
            ORDER BY timestamp DESC
        """, (user_id,))

        records = cursor.fetchall()

    if not records:
        print("📭 No transaction history found.")
        return

    print("\n--------- TRANSACTION HISTORY ---------")
    print(f"{'Type':<15}{'Amount':<15}{'Date'}")
    print("-" * 45)

    for t_type, amount, date in records:
        print(f"{t_type:<15}₦{amount:<14.2f}{date}")

    print("-" * 45)

def transfer(sender_id, sender_account):
    try:
        recipient_account = input("Enter recipient account number: ").strip()

        if recipient_account == sender_account:
            print("❌ You cannot transfer to your own account.")
            return

        amount = float(input("Enter transfer amount: ₦"))

        if amount <= 0:
            print("❌ Invalid transfer amount.")
            return

        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()

            # Sender balance
            cursor.execute(
                "SELECT balance FROM customer_info WHERE id = ?",
                (sender_id,)
            )
            sender_balance = cursor.fetchone()[0]

            if amount > sender_balance:
                print("❌ Insufficient balance.")
                return

            # Recipient lookup
            cursor.execute(
                "SELECT id, balance FROM customer_info WHERE account_number = ?",
                (recipient_account,)
            )
            recipient = cursor.fetchone()

            if not recipient:
                print("❌ Recipient account not found.")
                return

            recipient_id, recipient_balance = recipient

            # Update balances
            cursor.execute(
                "UPDATE customer_info SET balance = ? WHERE id = ?",
                (sender_balance - amount, sender_id)
            )

            cursor.execute(
                "UPDATE customer_info SET balance = ? WHERE id = ?",
                (recipient_balance + amount, recipient_id)
            )

            # Transactions
            cursor.execute("""
                INSERT INTO transactions (user_id, type, amount, target_account)
                VALUES (?, 'transfer', ?, ?)
            """, (sender_id, amount, recipient_account))

            conn.commit()

        print("Processing transfer...")
        time.sleep(2)
        print("✅ Transfer completed successfully.")

    except ValueError:
        print("❌ Enter a valid amount.")
