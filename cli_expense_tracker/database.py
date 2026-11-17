import sqlite3

connection = sqlite3.connect("expenses.db")
cursor = connection.cursor()

cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price_cents INTEGER NOT NULL,
            category TEXT NOT NULL,
            note TEXT,
            date TEXT NOT NULL
        )
    """)

connection.commit()
connection.close()
