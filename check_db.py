import sqlite3

conn = sqlite3.connect("bank_database.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(transactions);")
columns = cursor.fetchall()

for col in columns:
    print(col)

conn.close()
