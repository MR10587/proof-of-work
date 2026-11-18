import sqlite3
import pytest
import sys


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
    parse_price_to_cents,
    main,
    _validate_month
)


@pytest.mark.parametrize(
    ("price", "expected_cents"),
    [
        ("0.10", 10),
        ("0.20", 20),
        ("1", 100),
        ("5", 500),
    ],
)
def test_parse_price_to_cents(price, expected_cents):
    assert parse_price_to_cents(price) == expected_cents


@pytest.mark.parametrize("price", ["0", "-5", "invalid", "1.001", "NaN"])
def test_parse_price_to_cents_rejects_invalid_values(price):
    with pytest.raises(ValueError):
        parse_price_to_cents(price)


@pytest.mark.parametrize("month", ["2026-13", "2026-02-30"])
def test__validate_month_rejects_invalid_month(month):
    with pytest.raises(ValueError):
        _validate_month(month)


def test_main_add_prints_new_expense(monkeypatch, capsys):
    connection = sqlite3.connect(":memory:")
    monkeypatch.setattr("spend.get_connection", lambda: connection)
    captured_arguments = {}

    def fake_add_expense(connection, price_cents, category, note, date):
        captured_arguments.update(
            price_cents=price_cents,
            category=category,
            note=note,
            date=date,
        )
        return {
            "id": 1,
            "price_cents": price_cents,
            "category": category,
            "note": note,
            "date": date,
        }

    monkeypatch.setattr("spend.add_expense", fake_add_expense)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "spend.py",
            "spend",
            "add",
            "0.10",
            "--cat",
            "Food",
            "--note",
            "My",
            "breakfast",
            "--date",
            "2026-11-16",
        ],
    )

    exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "'price_cents': 10" in captured.out
    assert captured_arguments == {
        "price_cents": 10,
        "category": "Food",
        "note": "My breakfast",
        "date": "2026-11-16",
    }


def test_main_add_invalid_price_uses_exit_code_2(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "spend.py",
            "spend",
            "add",
            "-5",
            "--cat",
            "Food",
            "--note",
            "Snack",
            "--date",
            "2026-11-16",
        ],
    )

    exit_code = main()

    captured = capsys.readouterr()
    assert exit_code == 2
    assert "Price must be greater than zero" in captured.err


def test_main_list_prints_expenses(monkeypatch, capsys):
    connection = sqlite3.connect(":memory:")
    monkeypatch.setattr("spend.get_connection", lambda: connection)
    expenses = [{
        "id": 1,
        "price_cents": 1000,
        "category": "Food",
        "note": "Breakfast",
        "date": "2026-11-03",
        }]

    def fake_list_expenses(connection, month):
        month = _validate_month(month)

        for expense in expenses:
            if expense["date"].startswith(month + "-"):
                return expense

    monkeypatch.setattr("spend.list_expenses", fake_list_expenses)
    monkeypatch.setattr(sys, "argv", ["spend.py", "spend", "list", "--month", "2026-11"])

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out.strip() == str(expenses[0])



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

    assert result == {
        "total_cents": 2500,
        "categories": [
            {"name": "Sport", "total_cents": 1500},
            {"name": "Food", "total_cents": 1000},
        ],
    }


def test_report_expenses_empty_month(db):
    result = report_expenses(db, "2026-11")

    assert result == {"total_cents": 0, "categories": []}


def test_report_expenses_sorts_categories_by_total_then_name(db):
    db.execute("""
            INSERT INTO expenses VALUES
                (1, 1000, "Sport", "Gym", "2026-11-12"),
                (2, 1000, "Food", "Lunch", "2026-11-13"),
                (3, 500, "Travel", "Taxi", "2026-11-14")
            """)

    result = report_expenses(db, "2026-11")

    assert result == {
        "total_cents": 2500,
        "categories": [
            {"name": "Food", "total_cents": 1000},
            {"name": "Sport", "total_cents": 1000},
            {"name": "Travel", "total_cents": 500},
        ],
    }


def test_main_report_prints_report(monkeypatch, capsys):
    connection = sqlite3.connect(":memory:")
    monkeypatch.setattr("spend.get_connection", lambda: connection)
    captured_month = {}
    report = {
        "total_cents": 2500,
        "categories": [
            {"name": "Sport", "total_cents": 1500},
            {"name": "Food", "total_cents": 1000},
        ],
    }

    def fake_report_expenses(connection, month):
        captured_month["month"] = month
        return report

    monkeypatch.setattr("spend.report_expenses", fake_report_expenses)
    monkeypatch.setattr(
        sys,
        "argv",
        ["spend.py", "spend", "report", "--month", "2026-11"],
    )

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured_month == {"month": "2026-11"}
    assert captured.out.strip() == str(report)


def test_main_report_invalid_month(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["spend.py", "spend", "report", "--month", "2026-13"],
    )

    exit_code = main()
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Invalid month: 2026-13" in captured.err


def test_delete_expense(db):
    db.execute("""
            INSERT INTO expenses VALUES
                (1, 1000, "Food", "My breakfast", "2026-11-16"),
                (2, 1500, "Sport", "My workout", "2026-11-12")
            """)

    delete_expense(db, expense_id=1)

    count = db.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]

    assert count == 1
