from dotenv import load_dotenv
import sqlite3
import os


def get_database_path():
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is not configured")

    return database_url


def get_connection():
    database_url = get_database_path()
    connection = sqlite3.connect(database_url)

    return connection


def initialize_database(connection):
    try:
        with connection:
            connection.execute("""
                    CREATE TABLE IF NOT EXISTS expenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        price_cents INTEGER NOT NULL,
                        category TEXT NOT NULL,
                        note TEXT,
                        date TEXT NOT NULL
                    )
                """)
    except sqlite3.Error as e:
        print(f"Database error: {e}")

    connection.commit()
