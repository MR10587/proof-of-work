import csv
import argparse
from decimal import Decimal, InvalidOperation
from datetime import date as date_type
import sys
from database import get_connection, initialize_database


def parse_price_to_cents(value):
    try:
        price = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"Invalid price: {value}") from error

    if not price.is_finite():
        raise ValueError(f"Invalid price: {value}")

    cents = price * 100
    if cents != cents.to_integral_value():
        raise ValueError("Price must not contain fractions of a cent")
    if cents <= 0:
        raise ValueError("Price must be greater than zero")

    return int(cents)


def add_sub_parser(subparsers):
    add_parser = subparsers.add_parser("add", help="add an expense")
    add_parser.add_argument("price", help="price in dollars")
    add_parser.add_argument(
        "--cat",
        "--category",
        dest="category",
        required=True,
        help="expense category",
    )
    add_parser.add_argument(
        "--note",
        nargs="+",
        default=[],
        help="expense note",
    )
    add_parser.add_argument("--date", required=True, help="expense date (YYYY-MM-DD)")

    return subparsers


def list_sub_parser(subparsers):
    list_parser = subparsers.add_parser("list", help="list expenses by month")
    list_parser.add_argument("--month", required=True, help="expense month")

    return subparsers


def report_sub_parser(subparsers):
    report_parser = subparsers.add_parser("report", help="report expenses by month")
    report_parser.add_argument("--month", required=True, help="expense month")

    return subparsers


def delete_sub_parser(subparsers):
    delete_parser = subparsers.add_parser("delete", help="delete expense by id")
    delete_parser.add_argument("id", help="id of expense")

    return subparsers


def build_parser():
    parser = argparse.ArgumentParser(prog="spend")
    parser.add_argument("spend", choices=("spend",), help="command name")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = add_sub_parser(subparsers)
    list_parser = list_sub_parser(subparsers)
    report_parser = report_sub_parser(subparsers)
    delete_parser = delete_sub_parser(subparsers)

    return parser


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


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "add":
        try:
            price_cents = parse_price_to_cents(args.price)
        except ValueError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 2

        connection = get_connection()
        try:
            initialize_database(connection)
            try:
                result = add_expense(
                    connection,
                    price_cents=price_cents,
                    category=args.category,
                    note=" ".join(args.note),
                    date=args.date,
                )
            except ValueError as error:
                print(f"Error: {error}", file=sys.stderr)
                return 2
            print(result)
            return 0
        finally:
            connection.close()

    elif args.command == "list":
        try:
            month = _validate_month(args.month)
        except ValueError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 2

        connection = get_connection()

        try:
            initialize_database(connection)

            try:
                result = list_expenses(connection, month)
            except ValueError as error:
                print(f"Error: {error}", file=sys.stderr)
                return 2
            print(result)
            return 0
        finally:
            connection.close()

    elif args.command == "report":
        try:
            month = _validate_month(args.month)
        except ValueError as error:
            print(f"Error: {error}", file=sys.stderr)
            return 2

        connection = get_connection()

        try:
            initialize_database(connection)

            try:
                result = report_expenses(connection, month)
            except ValueError as error:
                print(f"Error: {error}", file=sys.stderr)
                return 2
            print(result)
            return 0
        finally:
            connection.close()

    elif args.command == "delete":
        try:
            id = int(args.id)
        except (ValueError, TypeError):
            print("Invalid id")
            return 2

        if id <= 0:
            return 2

        connection = get_connection()

        try:
            initialize_database(connection)

            result = delete_expense(connection, id)

            print(result)
            if result == 0:
                return 2
            return 0
        finally:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
