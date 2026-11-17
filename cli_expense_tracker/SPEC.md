Goal: Command line tool that track expenses by category and month in local file

Non-goals: multi-user, currencies, a GUI, syncing

Inputs and Outputs: Command name: spend
    1: spend add {price} --{category} --note {note} --date {date} (Add price of expense to the category with note at date)
    2: spend list --month {year-month} (Shows expenses in month)
    3: spend report --month {year-month} (Shows total and sub-total expense per category, in descending order)
    4: spend delete {id} (Deletes expense by id)
    5: spend export --format CSV (datani csv faylinda export edir)

Rules:
    1: Store amounts as integer, not float (12,50 dollar becomes 1250 cent)
    2: Data is kept in local JSON or sqlite file. File path comes from .env file
    3: Reject 0 or negative, invalid dates with exit code 2 and clear message
    4: Writes must not corrupt the file if the program is interrupted (write to a temp file, then rename, or use SQLite transactions).

Acceptance Criteria:
    1: spend add 0.10 --cat food followed by spend add 0.20 --cat food then spend report shows exactly 0.30 for food (no float drift).
    2: spend add -5 --cat food exits with code 2 and prints an error to stderr.
    spend add 5 --date 2026-02-30 is rejected as an invalid date.
    Killing the process during a write leaves the previous data file intact (demonstrated by a test).
    spend export --format csv correctly quotes a note containing a comma and a double quote.
    spend report for a month with no data prints a zero total, not an error.
    At least 12 automated tests pass with one command from a clean clone.
    README quick start works on a machine that is not yours.