This project is for managing personal expenses using cli commands.
Main commands are:
    1: spend add {price} --{category} --note {note} --date {date} (Add price of expense to the category with note at date)
    2: spend list --month {year-month} (Shows expenses in month)
    3: spend report --month {year-month} (Shows total and sub-total expense per category, in descending order)
    4: spend delete {id} (Deletes expense by id)
    5: spend export --format CSV (Export data to csv file)

Project is created using python and sqlite database
Testing covered by pytest library