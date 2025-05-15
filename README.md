# smart_expense_tracker

SECTION 1: Imports
import tkinter as tk
from tkinter import ttk, messagebox
tkinter → The base library for making GUI apps in Python.

ttk → Provides styled widgets (modern versions of buttons, labels, etc.).
messagebox → Used to show pop-up dialogs like "Success!" or "Error".

import sqlite3
Allows Python to connect to an SQLite database for persistent storage.

from datetime import datetime, date
datetime → For exact timestamps (date and time).

date → For just the current date (used in daily summary).

import csv
Used to export your expense data to a .csv file for Excel or Google Sheets.

from collections import defaultdict
Like a normal dictionary, but with a default value (like 0 for floats).

Used to group expenses by category easily.

SECTION 2: Database Initialization
DB_NAME = "expenses.db"
This is the filename for the SQLite database that will store your expenses.

def init_db():
    conn = sqlite3.connect(DB_NAME)
Connects to the SQLite database file. If it doesn’t exist, it's created.

    cur = conn.cursor()
A cursor lets you execute SQL commands in the database.

    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            description TEXT,
            timestamp TEXT
        )
    ''')
Creates the expenses table if it doesn’t already exist, with:

id → Auto-incrementing primary key

amount → How much you spent (₹)

category → Like 'food', 'rent', etc.

description → Short text like 'Uber to home'

timestamp → When it was added

    conn.commit()
    conn.close()
commit() saves changes to the DB.

close() closes the connection.

 SECTION 3: Add Expense to DB
def add_expense_to_db(amount, category, description):
This function stores a new expense in the database.

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
Opens the database and gets a cursor.

    cur.execute("INSERT INTO expenses (amount, category, description, timestamp) VALUES (?, ?, ?, ?)",
                (amount, category.lower(), description, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
Inserts a new row into expenses with:

amount

category (converted to lowercase for consistency)

description

Current timestamp in format: 2025-05-13 14:23:01

    conn.commit()
    conn.close()
Saves and closes the database connection.

SECTION 4: Add Expense from GUI
def add_expense():
This function gets data from input fields and adds it.

    try:
        amt = float(amount_entry.get())
Reads the amount typed into the entry box and converts it to a number.

        cat = category_entry.get().strip()
        desc = description_entry.get().strip()
Reads the category and description and removes extra spaces.

        if not cat or not desc:
            raise ValueError("Category and Description cannot be empty.")
Prevents empty values from being added.

        add_expense_to_db(amt, cat, desc)
Calls the previous function to store data.

        messagebox.showinfo("Success", f"Added ₹{amt} to {cat}")
Shows a success popup like “Added ₹300 to groceries”.

        amount_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)
Clears the input fields after successful entry.

    except ValueError as e:
        messagebox.showerror("Input Error", str(e))
If the amount is not a number or fields are blank, shows an error popup.

SECTION 5: Daily Summary
def show_daily_summary():
Displays all expenses made today.

    today = date.today().isoformat()
Gets today’s date in format: YYYY-MM-DD

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT amount, category FROM expenses WHERE date(timestamp) = ?", (today,))
    rows = cur.fetchall()
    conn.close()
Selects all records from today's date.

    summary = defaultdict(float)
    total = 0
summary groups totals by category.

    for amt, cat in rows:
        summary[cat] += amt
        total += amt
Adds each amount to its category and running total.

    result = f"Today: {today}\n\n"
    for cat, amt in summary.items():
        result += f"{cat.title()}: ₹{amt}\n"
    result += f"\nTotal: ₹{total}"
Builds the summary message string.

    if total > 1000:
        result += "\n High spending today!"
Adds a warning if daily spending exceeds ₹1000.

    show_result("Daily Summary", result)
Opens a new window to show the summary.

SECTION 6: Monthly Summary (Same logic)
def show_monthly_summary():
Shows total spending for the current month.

    month = datetime.now().strftime("%Y-%m")
Gets format 2025-05 (current year and month).

    cur.execute("SELECT amount, category FROM expenses WHERE strftime('%Y-%m', timestamp) = ?", (month,))
Gets all expenses matching that month.

The rest is same as daily summary but on a monthly scale.

SECTION 7: Recurring Expense Detector
def detect_recurring_expenses():
Detects descriptions that appear multiple times.

    cur.execute("SELECT description, COUNT(*) FROM expenses GROUP BY description HAVING COUNT(*) >= 2")
Groups by description and returns those used 2+ times.

    if not rows:
        show_result("Recurring Expenses", "No recurring expenses found.")
If nothing is found, show that.

    result = "Recurring Expenses:\n\n"
    for desc, count in rows:
        result += f"{desc} — {count} times\n"
Shows output like:

Uber — 3 times
Netflix — 2 times

SECTION 8: Export to CSV
def export_to_csv():
    ...
Selects all rows from expenses.

    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Amount', 'Category', 'Description', 'Timestamp'])
        writer.writerows(rows)
Writes everything into expenses.csv.

SECTION 9: Popup Window
def show_result(title, message):
Reusable popup for summaries and recurring expense messages.

    top = tk.Toplevel(root)
    ...
Opens a new child window with the provided message inside a Text widget.

SECTION 10: GUI Layout
root = tk.Tk()
root.title("Smart Expense Tracker")
root.geometry("420x400")
root.resizable(False, False)
Main app window setup with fixed size and title.

title_label = ttk.Label(root, text="Smart Expense Tracker", font=("Helvetica", 16, "bold"))
Bold title at the top of the app.

form_frame = ttk.Frame(root)
form_frame.pack(pady=10)
Frame holds the three input fields.

amount_entry = ttk.Entry(form_frame)
category_entry = ttk.Entry(form_frame)
description_entry = ttk.Entry(form_frame)
Input boxes to enter your data.

add_button = ttk.Button(root, text="Add Expense", command=add_expense)
Calls add_expense() when clicked.

ttk.Button(btn_frame, text="Daily Summary", command=show_daily_summary)
ttk.Button(btn_frame, text="Monthly Summary", command=show_monthly_summary)
ttk.Button(btn_frame, text="Recurring", command=detect_recurring_expenses)
ttk.Button(btn_frame, text="Export to CSV", command=export_to_csv)
Summary & export buttons.

FINAL LINE
root.mainloop()
Starts the GUI app and waits for user input.
* overlook of output:
  
  ![Screenshot (11)](https://github.com/user-attachments/assets/196da7a5-6cf4-4739-b833-734eeaf3fd5e)
  
  ![Screenshot (14)](https://github.com/user-attachments/assets/d351996a-1424-42d0-85ec-fbcf898be83c)

  ![Screenshot (15)](https://github.com/user-attachments/assets/cd38aba0-8285-43a7-b924-5dbea4365bec)


  
