
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
import csv
from collections import defaultdict

DB_NAME = "expenses.db"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            description TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_expense_to_db(amount, category, description):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO expenses (amount, category, description, timestamp) VALUES (?, ?, ?, ?)",
                (amount, category.lower(), description, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

# ---------- GUI FUNCTIONS ----------
def add_expense():
    try:
        amt = float(amount_entry.get())
        cat = category_entry.get().strip()
        desc = description_entry.get().strip()
        if not cat or not desc:
            raise ValueError("Category and Description cannot be empty.")
        add_expense_to_db(amt, cat, desc)
        messagebox.showinfo("Success", f"Added ₹{amt} to {cat}")
        amount_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        description_entry.delete(0, tk.END)
    except ValueError as e:
        messagebox.showerror("Input Error", str(e))

def show_daily_summary():
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT amount, category FROM expenses WHERE date(timestamp) = ?", (today,))
    rows = cur.fetchall()
    conn.close()

    summary = defaultdict(float)
    total = 0
    for amt, cat in rows:
        summary[cat] += amt
        total += amt

    result = f"Today: {today}\n\n"
    for cat, amt in summary.items():
        result += f"{cat.title()}: ₹{amt}\n"
    result += f"\nTotal: ₹{total}"

    if total > 1000:
        result += "\n High spending today!"

    show_result("Daily Summary", result)

def show_monthly_summary():
    month = datetime.now().strftime("%Y-%m")
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT amount, category FROM expenses WHERE strftime('%Y-%m', timestamp) = ?", (month,))
    rows = cur.fetchall()
    conn.close()

    summary = defaultdict(float)
    total = 0
    for amt, cat in rows:
        summary[cat] += amt
        total += amt

    result = f"Month: {month}\n\n"
    for cat, amt in summary.items():
        result += f"{cat.title()}: ₹{amt}\n"
    result += f"\nTotal: ₹{total}"
    show_result("Monthly Summary", result)

def detect_recurring_expenses():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT description, COUNT(*) FROM expenses GROUP BY description HAVING COUNT(*) >= 2")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        show_result("Recurring Expenses", "No recurring expenses found.")
        return

    result = "Recurring Expenses:\n\n"
    for desc, count in rows:
        result += f"{desc} — {count} times\n"
    show_result("Recurring Expenses", result)

def export_to_csv():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM expenses")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        messagebox.showinfo("No Data", "No expenses to export.")
        return

    filename = "expenses.csv"
    with open(filename, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Amount', 'Category', 'Description', 'Timestamp'])
        writer.writerows(rows)
    messagebox.showinfo("Exported", f"Expenses exported to {filename}")

def show_result(title, message):
    top = tk.Toplevel(root)
    top.title(title)
    top.geometry("400x400")
    txt = tk.Text(top, wrap="word")
    txt.insert(tk.END, message)
    txt.config(state="disabled")
    txt.pack(expand=True, fill="both", padx=10, pady=10)

# ---------- GUI SETUP ----------
init_db()

root = tk.Tk()
root.title("Smart Expense Tracker")
root.geometry("420x400")
root.resizable(False, False)

# Title
title_label = ttk.Label(root, text="Smart Expense Tracker", font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)

# Form
form_frame = ttk.Frame(root)
form_frame.pack(pady=10)

ttk.Label(form_frame, text="Amount (₹):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
amount_entry = ttk.Entry(form_frame)
amount_entry.grid(row=0, column=1, pady=5)

ttk.Label(form_frame, text="Category:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
category_entry = ttk.Entry(form_frame)
category_entry.grid(row=1, column=1, pady=5)

ttk.Label(form_frame, text="Description:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
description_entry = ttk.Entry(form_frame)
description_entry.grid(row=2, column=1, pady=5)

add_button = ttk.Button(root, text="Add Expense", command=add_expense)
add_button.pack(pady=10)

# Action Buttons
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="Daily Summary", command=show_daily_summary).grid(row=0, column=0, padx=5)
ttk.Button(btn_frame, text="Monthly Summary", command=show_monthly_summary).grid(row=0, column=1, padx=5)
ttk.Button(btn_frame, text="Recurring", command=detect_recurring_expenses).grid(row=1, column=0, padx=5, pady=5)
ttk.Button(btn_frame, text="Export to CSV", command=export_to_csv).grid(row=1, column=1, padx=5, pady=5)

# Run GUI
root.mainloop()
