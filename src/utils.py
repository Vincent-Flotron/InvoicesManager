import sqlite3
from models import Account, Invoice, Operation
from tkinter import messagebox
import os
import subprocess
import shutil

def create_tables(conn):
    c = get_cursor(conn)
    c.execute("""CREATE TABLE IF NOT EXISTS accounts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, bank_name TEXT, account_number TEXT UNIQUE)""")
    c.execute("""CREATE TABLE IF NOT EXISTS invoices
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, primary_receiver TEXT, receiver_name TEXT, receiver_address TEXT, receiver_account TEXT, primary_reference TEXT, secondary_reference TEXT, invoice_date TEXT, due_date TEXT, paid_date TEXT, amount REAL, paying_account_id INTEGER, file_path TEXT, remark TEXT, description TEXT, note TEXT, tag TEXT, category TEXT, 
                 FOREIGN KEY(paying_account_id) REFERENCES accounts(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS operations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, paid_date TEXT, income REAL DEFAULT 0, outcome REAL DEFAULT 0, account_id INTEGER, invoice_id INTEGER, 
                 FOREIGN KEY(account_id) REFERENCES accounts(id), 
                 FOREIGN KEY(invoice_id) REFERENCES invoices(id))""")
    commit_if_connection(conn)


# Invoices
def fetch_invoices(conn):
    c = get_cursor(conn)
    c.execute("SELECT * FROM invoices")
    rows = c.fetchall()
    invoices = []
    for row in rows:
        invoice = Invoice(*row)
        invoices.append(invoice)
    return invoices

def fetch_invoice_by_id(conn, invoice_id):
    c = get_cursor(conn)
    c.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,))
    row = c.fetchone()
    if row:
        return Invoice(*row)
    return None

def insert_invoice(conn, invoice):
    c = get_cursor(conn)
    c.execute("INSERT INTO invoices (primary_receiver, receiver_name, receiver_address, receiver_account, primary_reference, secondary_reference, invoice_date, due_date, paid_date, amount, paying_account_id, file_path, remark, description, note, tag, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (invoice.primary_receiver, invoice.receiver_name, invoice.receiver_address, invoice.receiver_account, invoice.primary_reference, invoice.secondary_reference, invoice.invoice_date, invoice.due_date, invoice.paid_date, invoice.amount, invoice.paying_account_id, invoice.file_path, invoice.remark, invoice.description, invoice.note, invoice.tag, invoice.category))
    invoice.id = c.lastrowid
    # Create a new operation
    if invoice.as_paying_account()   \
        and invoice.is_paid():
        insert_operation_from_invoice(conn.cursor(), invoice)
    commit_if_connection(conn)
    return c.lastrowid

def update_invoice(conn, invoice):
    # c = conn.cursor()
    c = get_cursor(conn)
    c.execute("UPDATE invoices SET primary_receiver=?, receiver_name=?, receiver_address=?, receiver_account=?, primary_reference=?, secondary_reference=?, invoice_date=?, due_date=?, paid_date=?, amount=?, paying_account_id=?, file_path=?, remark=?, description=?, note=?, tag=?, category=? WHERE id=?", (invoice.primary_receiver, invoice.receiver_name, invoice.receiver_address, invoice.receiver_account, invoice.primary_reference, invoice.secondary_reference, invoice.invoice_date, invoice.due_date, invoice.paid_date, invoice.amount, invoice.paying_account_id, invoice.file_path, invoice.remark, invoice.description, invoice.note, invoice.tag, invoice.category, invoice.id))
    # Update related operation if exists
    recorded_invoice = fetch_invoice_by_id(conn.cursor(), invoice.id)
    related_operation_was_updated = update_related_operation(conn.cursor(), recorded_invoice, invoice)

    # Create a new operation
    if not related_operation_was_updated \
       and invoice.as_paying_account()   \
       and invoice.is_paid():
        insert_operation_from_invoice(conn.cursor(), invoice)

    commit_if_connection(conn)

def update_related_operation(conn, recorded_invoice, invoice):
    relative_operation = fetch_operation_by_invoice_id(conn, invoice.id)
    has_relative_operation = False
    account_is_changing = recorded_invoice.paying_account_id != invoice.paying_account_id
    amount_is_changing = recorded_invoice.amount != invoice.amount
    paid_date_is_changing = recorded_invoice.paid_date != invoice.paid_date
    if relative_operation:
        if account_is_changing:
            update_operation_account_from_invoice(conn, invoice)
        if amount_is_changing:
            update_operation_outcome_from_invoice(conn, invoice)
        if paid_date_is_changing:
            update_operation_paid_date_from_invoice(conn, invoice)
        has_relative_operation = True

        if not invoice.paying_account_id \
            or not invoice.amount        \
            or not invoice.paid_date:
            delete_operation(conn, relative_operation.id)
            has_relative_operation = False

    commit_if_connection(conn)
    return has_relative_operation

def delete_invoice(conn, invoice_id):
    c = get_cursor(conn)
    c.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))
    commit_if_connection(conn)

def filter_invoices(conn, search_term):
    c = get_cursor(conn)
    c.execute("SELECT * FROM invoices WHERE primary_receiver LIKE ? OR receiver_name LIKE ? OR receiver_address LIKE ? OR receiver_account LIKE ? OR primary_reference LIKE ? OR secondary_reference LIKE ? OR description LIKE ? OR note LIKE ? OR tag LIKE ? OR category LIKE ?", ('%' + search_term + '%',) * 10)
    rows = c.fetchall()
    invoices = []
    for row in rows:
        invoice = Invoice(*row)
        invoices.append(invoice)
    return invoices

# General
def query(conn, query):
    c = get_cursor(conn)
    c.execute(query)
    rows = c.fetchall()
    return rows

# Accounts
def fetch_accounts(conn):
    c = get_cursor(conn)
    c.execute("SELECT * FROM accounts")
    rows = c.fetchall()
    accounts = []
    for row in rows:
        account = Account(*row)
        accounts.append(account)
    return accounts

def fetch_account_by_id(conn, account_id):
    c = get_cursor(conn)
    c.execute("SELECT * FROM accounts WHERE id=?", (account_id,))
    row = c.fetchone()
    if row:
        return Account(*row)
    
def fetch_account_by_description(conn, description):
    c = get_cursor(conn)
    c.execute("SELECT * FROM accounts WHERE description = ?", (description,))
    row = c.fetchone()
    if row:
        return Account(*row)
    return None

def insert_account(conn, account):
    c = get_cursor(conn)
    c.execute("INSERT INTO accounts (description, bank_name, account_number) VALUES (?, ?, ?)", (account.description, account.bank_name, account.iban))
    commit_if_connection(conn)

def update_account(conn, account):
    c = get_cursor(conn)
    c.execute("UPDATE accounts SET description=?, bank_name=?, account_number=? WHERE id=?", (account.description, account.bank_name, account.iban, account.id))
    commit_if_connection(conn)

def update_operation_outcome_from_invoice(conn, invoice):
    """
    Update the operation associated with an invoice when the invoice is paid.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        invoice (Invoice): The invoice object that has been paid.
    """
    if not invoice.is_paid:
        raise Exception("Invoice is not paid !")
    c = get_cursor(conn)

    # Check if an operation already exists for the invoice
    c.execute("SELECT id FROM operations WHERE invoice_id = ?", (invoice.id,))
    existing_operation = c.fetchone()

    if existing_operation:
        # Update the existing operation
        operation_id = existing_operation[0]
        c.execute("UPDATE operations SET outcome = ? WHERE id = ?", (invoice.amount, operation_id))
    else:
        # Insert a new operation
        c.execute("INSERT INTO operations (outcome, account_id, invoice_id) VALUES (?, ?, ?)",
                  (invoice.amount, invoice.paying_account_id, invoice.id))

    commit_if_connection(conn)

def update_operation_paid_date_from_invoice(conn, invoice):
    """
    Update the operation's paid date associated with an invoice.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        invoice (Invoice): The invoice object that has been paid.
    """
    c = get_cursor(conn)

    # Check if an operation already exists for the invoice
    c.execute("SELECT id FROM operations WHERE invoice_id = ?", (invoice.id,))
    existing_operation = c.fetchone()

    if existing_operation:
        # Update the existing operation
        operation_id = existing_operation[0]
        c.execute("UPDATE operations SET paid_date = ? WHERE id = ?", (invoice.paid_date, operation_id))
    else:
        # Insert a new operation
        c.execute("INSERT INTO operations (outcome, account_id, invoice_id) VALUES (?, ?, ?)",
                  (invoice.amount, invoice.paying_account_id, invoice.id))

    commit_if_connection(conn)

def update_operation_account_from_invoice(conn, invoice):
    """
    Update the operation associated with an invoice when the invoice is paid.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        invoice (Invoice): The invoice object that has been paid.
    """
    if not invoice.is_paid:
        raise Exception("Invoice is not paid !")
    c = get_cursor(conn)

    # Check if an operation already exists for the invoice
    c.execute("SELECT id FROM operations WHERE invoice_id = ?", (invoice.id,))
    existing_operation = c.fetchone()

    if existing_operation:
        # Update the existing operation
        operation_id = existing_operation[0]
        c.execute("UPDATE operations SET account_id = ? WHERE id = ?", (invoice.paying_account_id, operation_id))
    commit_if_connection(conn)

def delete_account(conn, account_id):
    c = get_cursor(conn)
    c.execute("DELETE FROM accounts WHERE id=?", (account_id,))
    commit_if_connection(conn)

# Operations
def fetch_operations(conn):
    c = get_cursor(conn)
    c.execute("SELECT * FROM operations ORDER BY paid_date")
    rows = c.fetchall()
    operations = []
    for row in rows:
        operation = Operation(*row)
        operations.append(operation)
    return operations

def fetch_operation_by_id(conn, operations_id):
    c = get_cursor(conn)
    c.execute("SELECT * FROM operations WHERE id=?", (operations_id,))
    row = c.fetchone()
    if row:
        return Operation(*row)
    return None

def fetch_operation_by_invoice_id(conn, invoice_id):
    c = get_cursor(conn)
    c.execute("SELECT * FROM operations WHERE invoice_id=?", (invoice_id,))
    rows = c.fetchall()
    if len(rows) > 1:
        raise Exception(f"Error: more than one operation for the invoice with id '{invoice_id}'")
    row = None
    if rows:
        row = rows[0]
    if row:
        return Operation(*row)
    return None

def fetch_operations_by_type(conn, operation_type):
    c = get_cursor(conn)
    c.execute("SELECT * FROM operations WHERE type = ?", (operation_type,))
    rows = c.fetchall()
    return [Operation(*row) for row in rows]

def insert_operation_from_invoice(conn, invoice):
    operation = Operation(
        type       = 'invoice',
        paid_date  = invoice.paid_date,
        income     = 0,
        outcome    = invoice.amount,
        account_id = invoice.paying_account_id,
        invoice_id = invoice.id
    )
    insert_operation(conn, operation)
    commit_if_connection(conn)

def insert_operation(conn, operation):
    c = get_cursor(conn)
    c.execute("INSERT INTO operations (paid_date, income, outcome, account_id, invoice_id, type) VALUES (?, ?, ?, ?, ?, ?)", (operation.paid_date, operation.income, operation.outcome, operation.account_id, operation.invoice_id, operation.type))
    commit_if_connection(conn)
    return None

def update_operation(conn, operation):
    c = get_cursor(conn)
    c.execute("UPDATE operations SET paid_date=?, income=?, outcome=?, account_id=?, invoice_id=?, type=? WHERE id=?", (operation.paid_date, operation.income, operation.outcome, operation.account_id, operation.invoice_id, operation.id, operation.type))
    commit_if_connection(conn)

def delete_operation(conn, operation_id):
    c = get_cursor(conn)
    c.execute("DELETE FROM operations WHERE id=?", (operation_id,))
    commit_if_connection(conn)


# Balance
def calculate_total_balance(conn):
    c = get_cursor(conn)
    c.execute("SELECT SUM(income) AS total_income, SUM(outcome) AS total_outcome FROM operations")
    row = c.fetchone()
    return row[0] or 0, row[1] or 0


# Transaction's management
def get_cursor(conn):
    _type = type(conn)
    # Get cursor from connection
    if _type == sqlite3.Connection:
        return conn.cursor()
    # Pass cursor
    elif _type == sqlite3.Cursor:
        return conn

def commit_if_connection(conn):
    _type = type(conn)
    if _type == sqlite3.Connection:
        conn.commit()


# Linked documents
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






# Backup
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
