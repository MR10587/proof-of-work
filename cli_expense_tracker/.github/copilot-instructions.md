# Copilot instructions

## Project scope

This project is a local, single-user command-line expense tracker. The command name is
`spend`. It is not intended to provide multi-user support, currency conversion, a GUI, or
synchronization.

## Implementation choices

- Implement the application in Python.
- Use the Python standard library for command-line parsing and other core functionality.
- Use SQLite as the local persistence backend.
- Categories are free-form, but must be non-empty and safely handled by the CLI and
  database layer.

## Command contract

Preserve the documented command surface:

- `spend add {price} --{category} --note {note} --date {date}` adds an expense.
- `spend list --month {year-month}` lists expenses for a month.
- `spend report --month {year-month}` shows the total and per-category subtotals in
  descending order.
- `spend delete {id}` deletes an expense by ID.
- `spend export --format csv` exports the data as CSV.

Follow the option spelling and behavior established in `SPEC.md`; do not introduce a
different command interface without updating the specification and its acceptance tests.

## Data and persistence

- Store monetary amounts as integer cents, never floating-point values. For example,
  `0.10` and `0.20` must report as exactly `0.30`.
- Keep data in a local SQLite file. The data-file path comes from `.env`.
- Writes must be interruption-safe: use an atomic temporary-file-and-rename strategy for
  file storage or SQLite transactions so an interrupted write leaves the previous data
  intact.
- CSV output must follow standard quoting rules, including notes containing commas or
  double quotes.

## Validation and output behavior

- Reject zero and negative amounts and invalid dates. Accept any non-empty category.
- These validation failures must exit with code `2` and print a clear message to stderr.
- A report for a month with no data prints a zero total rather than failing.

## Build, test, and lint commands

There is no implementation, package manifest, test suite, build configuration, or lint
configuration currently in this subproject, so these commands are not runnable yet.

- Use pytest for the test suite: `pytest`.
- Run one test with pytest's node ID selector:
  `pytest path\to\test_file.py::test_name`.

When the test suite is added, keep the acceptance criteria in `SPEC.md` covered by
automated tests and update this section with the verified clean-clone command.

## Acceptance criteria to preserve

The implementation and tests must cover:

- Exact cent arithmetic for repeated additions.
- Rejection of negative amounts with exit code `2` and stderr output.
- Rejection of impossible calendar dates such as `2026-02-30`.
- Preservation of the previous data file if a write is interrupted.
- Correct CSV quoting for notes containing commas and double quotes.
- A zero-valued report for an empty month.
- At least 12 automated tests runnable with one command from a clean clone.
- A README quick start that works on a clean machine.
