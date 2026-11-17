import csv
from datetime import date as date_type
import sys
from database import get_connection, initialize_database


def _validate_date(value):
    try:
        date_type.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Invalid date: {value}") from error


def _validate_month(month):
    try:
        parsed_month = date_type.fromisoformat(f"{month}-01")
    except (TypeError, ValueError) as error:
        raise ValueError(f"Invalid month: {month}") from error

    return parsed_month.strftime("%Y-%m")


def _row_to_dict(columns, row):
    return dict(zip(columns, row))


def add_expense(connection, price_cents, category, note, date):
    if price_cents <= 0:
        raise ValueError("Price must be greater than zero")
    if not category or not category.strip():
        raise ValueError("Category must not be empty")

    _validate_date(date)
    cursor = connection.execute(
        """
        INSERT INTO expenses (price_cents, category, note, date)
        VALUES (?, ?, ?, ?)
        """,
        (price_cents, category, note, date),
    )
    connection.commit()

    row = connection.execute(
        """
        SELECT id, price_cents, category, note, date
        FROM expenses
        WHERE id = ?
        """,
        (cursor.lastrowid,),
    ).fetchone()

    columns = ("id", "price_cents", "category", "note", "date")

    return _row_to_dict(columns, row)


def list_expenses(connection, month):
    month = _validate_month(month)
    cursor = connection.execute(
        """
        SELECT id, price_cents, category, note, date
        FROM expenses
        WHERE date LIKE ?
        ORDER BY price_cents DESC, id DESC
        """,
        (f"{month}-%",),
    )
    columns = [column[0] for column in cursor.description]
    return [_row_to_dict(columns, row) for row in cursor.fetchall()]


def report_expenses(connection, month):
    month = _validate_month(month)
    total = connection.execute(
        "SELECT COALESCE(SUM(price_cents), 0) FROM expenses WHERE date LIKE ?",
        (f"{month}-%",),
    ).fetchone()[0]
    categories = connection.execute(
        """
        SELECT category AS name, SUM(price_cents) AS total_cents
        FROM expenses
        WHERE date LIKE ?
        GROUP BY category
        ORDER BY total_cents DESC, name ASC
        """,
        (f"{month}-%",),
    ).fetchall()
    return {
        "total_cents": total,
        "categories": [{"name": row[0], "total_cents": row[1]} for row in categories],
    }


def delete_expense(connection, expense_id):
    cursor = connection.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    connection.commit()
    return cursor.rowcount


def export_to_csv(connection, output_path):
    rows = connection.execute(
        """
        SELECT id, price_cents, category, note, date
        FROM expenses
        ORDER BY date ASC, id ASC
        """
    ).fetchall()
    with open(output_path, "w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(("id", "price_cents", "category", "note", "date"))
        writer.writerows(rows)


def main():
    connection = get_connection()
    try:
        initialize_database(connection)

        if len(sys.argv) > 1:
            print(sys.argv[1])
    finally:
        connection.close()


if __name__ == "__main__":
    main()
