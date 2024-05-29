import sqlite3
from models import Account, Invoice, Operation
from tkinter import messagebox
import os
import subprocess
import shutil

def create_tables(conn):
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS accounts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, bank_name TEXT, account_number TEXT UNIQUE)""")
    c.execute("""CREATE TABLE IF NOT EXISTS invoices
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, primary_receiver TEXT, receiver_name TEXT, receiver_address TEXT, receiver_account TEXT, primary_reference TEXT, secondary_reference TEXT, invoice_date TEXT, due_date TEXT, paid_date TEXT, amount REAL, paying_account_id INTEGER, file_path TEXT, remark TEXT, description TEXT, note TEXT, tag TEXT, category TEXT, 
                 FOREIGN KEY(paying_account_id) REFERENCES accounts(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS operations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, income REAL DEFAULT 0, outcome REAL DEFAULT 0, account_id INTEGER, invoice_id INTEGER, 
                 FOREIGN KEY(account_id) REFERENCES accounts(id), 
                 FOREIGN KEY(invoice_id) REFERENCES invoices(id))""")
    conn.commit()

def insert_account(conn, account):
    c = conn.cursor()
    c.execute("INSERT INTO accounts (description, bank_name, account_number) VALUES (?, ?, ?)", (account.description, account.bank_name, account.account_number))
    conn.commit()

def insert_invoice(conn, invoice):
    c = conn.cursor()
    c.execute("INSERT INTO invoices (primary_receiver, receiver_name, receiver_address, receiver_account, primary_reference, secondary_reference, invoice_date, due_date, paid_date, amount, paying_account_id, file_path, remark, description, note, tag, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (invoice.primary_receiver, invoice.receiver_name, invoice.receiver_address, invoice.receiver_account, invoice.primary_reference, invoice.secondary_reference, invoice.invoice_date, invoice.due_date, invoice.paid_date, invoice.amount, invoice.paying_account_id, invoice.file_path, invoice.remark, invoice.description, invoice.note, invoice.tag, invoice.category))
    conn.commit()
    if invoice.paid_date:
        insert_operation(conn, Operation(outcome=invoice.amount, account_id=invoice.paying_account_id, invoice_id=c.lastrowid))

def insert_operation(conn, operation):
    c = conn.cursor()
    c.execute("INSERT INTO operations (income, outcome, account_id, invoice_id) VALUES (?, ?, ?, ?)", (operation.income, operation.outcome, operation.account_id, operation.invoice_id))
    conn.commit()

# Invoices
def fetch_invoices(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM invoices")
    rows = c.fetchall()
    invoices = []
    for row in rows:
        invoice = Invoice(*row)
        invoices.append(invoice)
    return invoices

def update_invoice(conn, invoice):
    c = conn.cursor()
    c.execute("UPDATE invoices SET primary_receiver=?, receiver_name=?, receiver_address=?, receiver_account=?, primary_reference=?, secondary_reference=?, invoice_date=?, due_date=?, paid_date=?, amount=?, paying_account_id=?, file_path=?, remark=?, description=?, note=?, tag=?, category=? WHERE id=?", (invoice.primary_receiver, invoice.receiver_name, invoice.receiver_address, invoice.receiver_account, invoice.primary_reference, invoice.secondary_reference, invoice.invoice_date, invoice.due_date, invoice.paid_date, invoice.amount, invoice.paying_account_id, invoice.file_path, invoice.remark, invoice.description, invoice.note, invoice.tag, invoice.category, invoice.id))
    conn.commit()

def delete_invoice(conn, invoice_id):
    c = conn.cursor()
    c.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))
    conn.commit()

# Accounts
def fetch_accounts(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM accounts")
    rows = c.fetchall()
    accounts = []
    for row in rows:
        account = Account(*row)
        accounts.append(account)
    return accounts

def update_account(conn, account):
    c = conn.cursor()
    c.execute("UPDATE accounts SET description=?, bank_name=?, account_number=? WHERE id=?", (account.description, account.bank_name, account.account_number, account.id))
    conn.commit()

def delete_account(conn, account_id):
    c = conn.cursor()
    c.execute("DELETE FROM accounts WHERE id=?", (account_id,))
    conn.commit()

# Operations
def fetch_operations(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM operations")
    rows = c.fetchall()
    operations = []
    for row in rows:
        operation = Operation(*row)
        operations.append(operation)
    return operations

def fetch_account_by_id(conn, account_id):
    c = conn.cursor()
    c.execute("SELECT * FROM accounts WHERE id=?", (account_id,))
    row = c.fetchone()
    if row:
        return Account(*row)
    return None

def fetch_invoice_by_id(conn, invoice_id):
    c = conn.cursor()
    c.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,))
    row = c.fetchone()
    if row:
        return Invoice(*row)
    return None

def fetch_operation_by_id(conn, operations_id):
    c = conn.cursor()
    c.execute("SELECT * FROM operations WHERE id=?", (operations_id,))
    row = c.fetchone()
    if row:
        return Operation(*row)
    return None

def update_operation(conn, operation):
    c = conn.cursor()
    c.execute("UPDATE operations SET income=?, outcome=?, account_id=?, invoice_id=? WHERE id=?", (operation.income, operation.outcome, operation.account_id, operation.invoice_id, operation.id))
    conn.commit()

def delete_operation(conn, operation_id):
    c = conn.cursor()
    c.execute("DELETE FROM operations WHERE id=?", (operation_id,))
    conn.commit()

def calculate_total_balance(conn):
    c = conn.cursor()
    c.execute("SELECT SUM(income) AS total_income, SUM(outcome) AS total_outcome FROM operations")
    row = c.fetchone()
    return row[0] or 0, row[1] or 0

def open_file(file_path):
    """
    Open a file with the default application associated with its file type.

    Args:
        file_path (str): The path of the file to be opened.
    """
    if os.path.isfile(file_path):
        try:
            if os.name == 'nt':  # Windows
                os.startfile(file_path)
            elif os.name == 'posix':  # Unix-based systems (Linux, macOS)
                subprocess.call(['xdg-open', file_path])
            else:
                print(f"Unable to open file: {file_path}")
        except Exception as e:
            print(f"Error opening file: {e}")
    else:
        print(f"File not found: {file_path}")





def filter_invoices(conn, search_term):
    c = conn.cursor()
    c.execute("SELECT * FROM invoices WHERE primary_receiver LIKE ? OR receiver_name LIKE ? OR receiver_address LIKE ? OR receiver_account LIKE ? OR primary_reference LIKE ? OR secondary_reference LIKE ? OR description LIKE ? OR note LIKE ? OR tag LIKE ? OR category LIKE ?", ('%' + search_term + '%',) * 10)
    rows = c.fetchall()
    invoices = []
    for row in rows:
        invoice = Invoice(*row)
        invoices.append(invoice)
    return invoices


def backup_database(conn, backup_dir, absolute_db_path):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    backup_file = os.path.join(backup_dir, "database_backup.db")
    shutil.copy(absolute_db_path, backup_file)

def restore_database(conn, backup_file, absolute_db_path):
    if os.path.exists(backup_file):
        shutil.copy(backup_file, absolute_db_path)
    else:
        messagebox.showerror("Error", "Backup file not found.")


# Add other CRUD operations for accounts, invoices, and operations
