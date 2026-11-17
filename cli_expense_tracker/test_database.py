import sqlite3

from database import get_connection, get_database_path, initialize_database


def test_get_database_path_reads_environment(monkeypatch, tmp_path):
    database_path = tmp_path / "expenses.db"
    monkeypatch.setenv("DATABASE_URL", str(database_path))

    assert get_database_path() == str(database_path)


def test_get_connection_uses_configured_path(monkeypatch, tmp_path):
    database_path = tmp_path / "expenses.db"
    monkeypatch.setenv("DATABASE_URL", str(database_path))

    connection = get_connection()
    try:
        assert isinstance(connection, sqlite3.Connection)
        assert connection.execute("SELECT 1").fetchone() == (1,)
    finally:
        connection.close()


def test_initialize_database_creates_expenses_table():
    connection = sqlite3.connect(":memory:")
    try:
        initialize_database(connection)

        columns = connection.execute("PRAGMA table_info(expenses)").fetchall()

        assert [column[1] for column in columns] == [
            "id",
            "price_cents",
            "category",
            "note",
            "date",
        ]
        assert connection.execute("SELECT 1").fetchone() == (1,)
    finally:
        connection.close()
