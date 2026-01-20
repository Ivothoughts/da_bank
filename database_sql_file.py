import sqlite3

with sqlite3.connect("bank_database.db") as conn:
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        account_number TEXT UNIQUE NOT NULL,
        balance REAL DEFAULT 0.0,
        date_and_time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        transaction_type TEXT CHECK (transaction_type IN ('Deposit','Withdrawal','Transfer')) NOT NULL,
        amount REAL NOT NULL,
        target_account TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES customer_info(id) ON DELETE CASCADE,
        FOREIGN KEY (target_account) REFERENCES customer_info(account_number) ON DELETE SET NULL
    )
    """)
