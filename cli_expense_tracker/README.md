This project is for managing personal expenses using cli commands.
Main commands are:
    1: spend add {price} --{category} --note {note} --date {date} (Add price of expense to the category with note at date)
    2: spend list --month {year-month} (Shows expenses in month)
    3: spend report --month {year-month} (Shows total and sub-total expense per category, in descending order)
    4: spend delete {id} (Deletes expense by id)
    5: spend export --format CSV (Export data to csv file)

Project is created using python and sqlite database
Testing covered by pytest library

<h2>🚀 Getting Started</h2>

<ol>
  <li>
    <p><strong>Clone the repository</strong> to your computer by running this command in your terminal:</p>
    <pre><code>git clone https://github.com</code></pre>
  </li>

  <li>
    <p><strong>Navigate into the project directory:</strong></p>
    <pre><code>cd proof-of-work/cli_expense_tracker</code></pre>
  </li>

  <li>
    <p><strong>Install the required packages:</strong></p>
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>

  <li>
    <p><strong>Set up your environment and database:</strong></p>
    <ul>
      <li>Create a <code>.env</code> file in the <code>cli_expense_tracker</code> root directory and copy the contents of <code>.env.example</code> into it.</li>
      <li>Create an empty file named <code>expenses.db</code> in the same root directory.</li>
      <li>Right-click <code>expenses.db</code> and select <strong>Copy Path</strong>.</li>
      <li>Open your <code>.env</code> file, replace <code>&lt;database_url&gt;</code> after the <code>=</code> sign with your copied path, and save the file.</li>
    </ul>
  </li>

  <li>
    <p><strong>Add your first expense:</strong> Run the following command in your terminal (you can customize the amount, category, note, and date, but make sure to keep the <code>--</code> flags):</p>
    <pre><code>py spend.py spend add 100 --category Food --note Breakfast --date 2026-03-08</code></pre>
  </li>

  <li>
    <p><strong>View your monthly expense history:</strong> Filter by month using the <code>YYYY-MM</code> format (do not include the day):</p>
    <pre><code>py spend.py spend list --month 2026-03</code></pre>
  </li>

  <li>
    <p><strong>Generate a monthly report:</strong> View your total spending broken down by category and overall for a specific month:</p>
    <pre><code>py spend.py spend report --month 2026-03</code></pre>
  </li>

  <li>
    <p><strong>Export your data to CSV:</strong> Before deleting anything, back up your database records into an <code>expenses.csv</code> file in your root directory:</p>
    <pre><code>py spend.py spend export --format CSV</code></pre>
  </li>

  <li>
    <p><strong>Delete an expense:</strong> Remove an entry by its ID (this will print the number of deleted records, e.g., <code>1</code>, to the screen):</p>
    <pre><code>py spend.py spend delete 1</code></pre>
  </li>
</ol>
