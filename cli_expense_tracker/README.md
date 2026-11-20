This project is for managing personal expenses using cli commands.
Main commands are:
    1: spend add {price} --{category} --note {note} --date {date} (Add price of expense to the category with note at date)
    2: spend list --month {year-month} (Shows expenses in month)
    3: spend report --month {year-month} (Shows total and sub-total expense per category, in descending order)
    4: spend delete {id} (Deletes expense by id)
    5: spend export --format CSV (Export data to csv file)

Project is created using python and sqlite database
Testing covered by pytest library

How you can start:
    1- clone the repository in your computer by running this command on terminal(git clone https://github.com/MR10587/proof-of-work)
    2- change directory into cli_expense_tracker by this command: (cd cli_expense_tracker)
    3- First of all, make sure to run (pip install requirements.txt) to install necessary packages
    4- create .env file in root directory and copy content of .env.example to this file. Then create expenses.db in your root directory. Then copy your .db file's path by right click + copy path. Then in .env file delete <database_url> after = sign and paste your copied path.
    5- You can now run commands to start. Start with adding expense: Paste this into terminal (py spend.py spend add 100 --category Food --note Breakfast --date 2026-03-08) You can change price, category name, note text, and date but make sure to keep words with -- at the beginning.
    6- To see your monthly expenses history, type this command into terminal (py spend.py spend list --month 2026-03) because you added expense for march I type 03, you can enter which date you want, but make sure it is in the format of YEAR-MONTH, not include days
    7- To see total expense by category and overall run this: (py spend.py spend report --month 2026-03)
    8- Before deleting lets try exporting as csv, run this command: (py spend.py spend export --format CSV), this command use your data in database to create expenses.csv file inside root directory
    9- To delete your expense data, just enter this command (py spend.py spend delete 1) This will print count of expenses deleted(which is 1) to the screen.
