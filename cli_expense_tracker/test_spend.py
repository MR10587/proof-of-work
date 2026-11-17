import sqlite3
import pytest


@pytest.fixture
def db():
    connection = sqlite3.connect(":memory:")

    connection.execute("""
        CREATE TABLE expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price_cents INTEGER NOT NULL,
            category TEXT NOT NULL,
            note TEXT,
            date TEXT NOT NULL
        )
    """)

    yield connection
    connection.close()


from spend import (
    add_expense,
    list_expenses,
    report_expenses,
    delete_expense,
    export_to_csv,
)


def test_add_expense(db):
    result = add_expense(
        db, price_cents=1000, category="Food", note="My breakfast", date="2026-11-16"
    )

    assert result["price_cents"] == 1000

    count = db.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]

    assert count == 1


def test_list_expenses(db):
    db.execute("""
        INSERT INTO expenses VALUES
            (1, 1000, "Food", "My breakfast", "2026-11-16"),
            (2, 1500, "Sport", "My workout", "2026-11-12")
        """)

    result = list_expenses(db, "2026-11")

    assert len(result) == 2
    assert result[0]["price_cents"] == 1500
    assert result[1]["price_cents"] == 1000


def test_report_expenses(db):
    db.execute("""
            INSERT INTO expenses VALUES
                (1, 1000, "Food", "My breakfast", "2026-11-16"),
                (2, 1500, "Sport", "My workout", "2026-11-12")
            """)

    result = report_expenses(db, "2026-11")

    assert result == {"total_cents": 2500, "categories": [{"name": "Sport", "total_cents": 1500}, {"name": "Food", "total_cents": 1000}]}


def test_delete_expense(db):
    db.execute("""
            INSERT INTO expenses VALUES
                (1, 1000, "Food", "My breakfast", "2026-11-16"),
                (2, 1500, "Sport", "My workout", "2026-11-12")
            """)

    delete_expense(db, expense_id=1)

    count = db.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]

    assert count == 1