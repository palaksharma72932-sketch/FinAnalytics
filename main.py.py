import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


# --- STEP 1: Database Setup ---
def init_db():
    conn = sqlite3.connect('FinAnalytics.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            category TEXT,
            amount REAL
        )
    ''')
    conn.commit()
    conn.close()


# --- STEP 2: Logic Functions ---
def auto_categorize(desc):
    desc = desc.lower()
    if any(word in desc for word in ['zomato', 'swiggy', 'food', 'restaurant', 'dinner', 'lunch']):
        return 'Food & Dining'
    elif any(word in desc for word in ['bill', 'recharge', 'electricity', 'water', 'gas']):
        return 'Utilities/Bills'
    elif any(word in desc for word in ['uber', 'petrol', 'auto', 'fuel', 'metro']):
        return 'Transport'
    elif 'rent' in desc:
        return 'Rent/Housing'
    elif any(word in desc for word in ['amazon', 'flipkart', 'shopping']):
        return 'Shopping'
    else:
        return 'Miscellaneous'


def record_transaction():
    desc = desc_entry.get().strip()
    amt = amt_entry.get().strip()
    date = datetime.now().strftime("%Y-%m-%d")

    if not desc or not amt:
        messagebox.showwarning("Input Validation", "Required fields are missing.")
        return

    try:
        amt = float(amt)
        cat = auto_categorize(desc)

        conn = sqlite3.connect('FinAnalytics.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO transactions (date, description, category, amount) VALUES (?, ?, ?, ?)',
                       (date, desc, cat, amt))
        conn.commit()
        conn.close()

        messagebox.showinfo("Success", f"Recorded under: {cat}")
        desc_entry.delete(0, tk.END)
        amt_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Data Error", "Please enter a valid numeric amount.")


def generate_insights():
    conn = sqlite3.connect('FinAnalytics.db')
    # Yahan hum wahi data fetch kar rahe hain jo actually database mein hai
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()

    if df.empty:
        messagebox.showinfo("No Records", "Please add transactions first.")
        return

    # Sirf wahi categories dikhayega jinki entries database mein hain
    cat_totals = df.groupby('category')['amount'].sum()

    plt.figure(figsize=(10, 5))

    # 1. Pie Chart (Modern Professional Colors)
    plt.subplot(1, 2, 1)
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
    cat_totals.plot(kind='pie', autopct='%1.1f%%', startangle=140, colors=colors, title='Expense Share')
    plt.ylabel('')

    # 2. Bar Chart (Daily Trend)
    plt.subplot(1, 2, 2)
    df.groupby('date')['amount'].sum().plot(kind='bar', color='#3498db', title='Spending Trend')
    plt.xlabel('Date')
    plt.ylabel('Total (INR)')

    plt.tight_layout()
    plt.show()


# --- STEP 3: Attractive GUI Interface ---
root = tk.Tk()
root.title("FinAnalytics Engine")
root.geometry("500x450")
root.configure(bg="#f0f3f5")

init_db()

# Main Container
main_frame = tk.Frame(root, bg="white", padx=40, pady=40, relief="flat", highlightbackground="#d1d8e0",
                      highlightthickness=1)
main_frame.place(relx=0.5, rely=0.5, anchor="center")

# Labels & Branding
tk.Label(main_frame, text="FINANALYTICS", font=("Segoe UI", 24, "bold"), fg="#2c3e50", bg="white").pack()
tk.Label(main_frame, text="Personal Expenditure Management", font=("Segoe UI", 9), fg="#95a5a6", bg="white").pack(
    pady=(0, 25))

# Input fields
tk.Label(main_frame, text="Description:", font=("Segoe UI", 10, "bold"), bg="white", fg="#34495e").pack(anchor="w")
desc_entry = tk.Entry(main_frame, font=("Segoe UI", 11), width=30, bg="#f8f9fa", relief="solid", bd=0)
desc_entry.pack(pady=(5, 15), ipady=5)

tk.Label(main_frame, text="Amount (INR):", font=("Segoe UI", 10, "bold"), bg="white", fg="#34495e").pack(anchor="w")
amt_entry = tk.Entry(main_frame, font=("Segoe UI", 11), width=30, bg="#f8f9fa", relief="solid", bd=0)
amt_entry.pack(pady=(5, 25), ipady=5)

# Buttons
record_btn = tk.Button(main_frame, text="RECORD TRANSACTION", command=record_transaction,
                       bg="#2ecc71", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=25, height=2,
                       cursor="hand2")
record_btn.pack(pady=5)

insight_btn = tk.Button(main_frame, text="GENERATE INSIGHTS", command=generate_insights,
                        bg="#3498db", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", width=25, height=2,
                        cursor="hand2")
insight_btn.pack(pady=5)

root.mainloop()