import tkinter as tk
from tkinter import ttk, filedialog
import sqlite3
from datetime import datetime
from models import Account, Invoice, Operation
from utils import create_tables, insert_account, insert_invoice, insert_operation, \
                  fetch_invoices, fetch_accounts, fetch_account_by_id, fetch_operations, \
                  open_file, fetch_invoice_by_id, calculate_total_balance, update_invoice, \
                  filter_invoices, backup_database, restore_database, delete_invoice

class InvoicesToPayView(tk.Frame):
    def __init__(self, parent, conn, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.conn = conn
        create_tables(conn)

        # Create UI elements
        self.tree = ttk.Treeview(self, columns=("id", "primary_receiver", "receiver_name", "receiver_address", "receiver_account", "primary_reference", "secondary_reference", "invoice_date", "due_date", "paid_date", "amount", "paying_account", "file_path", "remark", "description", "note", "tag", "category"), show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        # Configure columns
        self.tree.heading("primary_receiver", text="Primary Receiver")
        # Configure other columns...

        # Add buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x")

        add_button = tk.Button(button_frame, text="Add", command=self.add_invoice)
        add_button.pack(side="left")

        edit_button = tk.Button(button_frame, text="Edit", command=self.edit_invoice)
        edit_button.pack(side="left")

        delete_button = tk.Button(button_frame, text="Delete", command=self.delete_invoice)
        delete_button.pack(side="left")

        # Add a search entry and filter button
        search_frame = tk.Frame(self)
        search_frame.pack(side="top", fill="x")

        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True)

        filter_button = tk.Button(search_frame, text="Filter", command=self.filter_invoices)
        filter_button.pack(side="right")

        # Configure columns for sorting
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sort_column(c, None))
            self.tree.heading(col, anchor="center")


        # Populate the treeview
        self.populate_treeview()

    def populate_treeview(self, invoices=None):
        # Clear the treeview
        self.tree.delete(*self.tree.get_children())

        # Fetch invoices from the database or use provided invoices
        if invoices is None:
            invoices = fetch_invoices(self.conn)

        # Insert invoices into the treeview
        for invoice in invoices:
            self.tree.insert("", "end", values=(invoice.id, invoice.primary_receiver, invoice.receiver_name, invoice.receiver_address, invoice.receiver_account, invoice.primary_reference, invoice.secondary_reference, invoice.invoice_date, invoice.due_date, invoice.paid_date, invoice.amount, invoice.paying_account_id, invoice.file_path, invoice.remark, invoice.description, invoice.note, invoice.tag, invoice.category))

    def add_invoice(self):
        # Open a dialog to enter invoice details
        dialog = InvoiceDialog(self, title="Add Invoice")


    def edit_invoice(self):
        # Retrieve the selected invoice from the treeview
        selected = self.tree.focus()
        if selected:
            invoice_id = self.tree.item(selected)["values"][0]
            invoice = fetch_invoice_by_id(self.conn, invoice_id)
            dialog = InvoiceDialog(self, title="Edit Invoice", invoice=invoice)
            # if dialog.result:
            #     update_invoice(self.conn, dialog.result)
            #     self.populate_treeview()

    def delete_invoice(self):
        # Retrieve the selected invoice from the treeview
        selected = self.tree.focus()
        if selected:
            # Call delete_invoice() with the selected invoice id
            invoice_id = self.tree.item(selected)["values"][0]
            delete_invoice(self.conn, invoice_id)
            self.populate_treeview()

    def filter_invoices(self):
        search_term = self.search_entry.get().lower()
        filtered_invoices = filter_invoices(self.conn, search_term)
        self.populate_treeview(filtered_invoices)

    def sort_column(self, col, reverse):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children("")]
        data.sort(reverse=reverse)

        for index, item in enumerate(data):
            self.tree.move(item[1], "", index)

        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))


class AccountsView(tk.Frame):
    def __init__(self, parent, conn, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.conn = conn

        # Create UI elements
        self.tree = ttk.Treeview(self, columns=("description", "bank_name", "account_number"), show="headings")
        self.tree.pack(side="left", fill="both", expand=True)

        # Configure columns
        self.tree.heading("description", text="Description")
        self.tree.heading("bank_name", text="Bank Name")
        self.tree.heading("account_number", text="Account Number")

        # Add buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x")

        add_button = tk.Button(button_frame, text="Add", command=self.add_account)
        add_button.pack(side="left")

        edit_button = tk.Button(button_frame, text="Edit", command=self.edit_account)
        edit_button.pack(side="left")

        delete_button = tk.Button(button_frame, text="Delete", command=self.delete_account)
        delete_button.pack(side="left")

        # Populate the treeview
        self.populate_treeview()

    def populate_treeview(self):
        # Clear the treeview
        self.tree.delete(*self.tree.get_children())

        # Fetch accounts from the database
        accounts = fetch_accounts(self.conn)

        # Insert accounts into the treeview
        for account in accounts:
            self.tree.insert("", "end", values=(account.description, account.bank_name, account.account_number))

    def add_account(self):
        # Open a dialog to enter account details
        # Call insert_account() with the new account data
        self.populate_treeview()

    def edit_account(self):
        # Retrieve the selected account from the treeview
        selected = self.tree.focus()
        if selected:
            # Open a dialog to edit account details
            # Call update_account() with the updated account data
            self.populate_treeview()

    def delete_account(self):
        # Retrieve the selected account from the treeview
        selected = self.tree.focus()
        if selected:
            # Call delete_account() with the selected account id
            self.populate_treeview()


class OperationsView(tk.Frame):
    def __init__(self, parent, conn, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.conn = conn

        # Create UI elements
        self.tree = ttk.Treeview(self, columns=("income", "outcome", "account", "invoice", "file_path"), show="headings")
        self.tree.pack(side="top", fill="both", expand=True)

        # Configure columns
        self.tree.heading("income", text="Income")
        self.tree.heading("outcome", text="Outcome")
        self.tree.heading("account", text="Account")
        self.tree.heading("invoice", text="Invoice")
        self.tree.heading("file_path", text="File Path")

        # Add buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x")

        add_button = tk.Button(button_frame, text="Add", command=self.add_operation)
        add_button.pack(side="left")

        edit_button = tk.Button(button_frame, text="Edit", command=self.edit_operation)
        edit_button.pack(side="left")

        delete_button = tk.Button(button_frame, text="Delete", command=self.delete_operation)
        delete_button.pack(side="left")

        # Populate the treeview
        self.populate_treeview()

        # Bind double-click event to open file
        self.tree.bind("<Double-1>", self.open_file)

    def populate_treeview(self):
        # Clear the treeview
        self.tree.delete(*self.tree.get_children())

        # Fetch operations from the database
        operations = fetch_operations(self.conn)

        # Insert operations into the treeview
        for operation in operations:
            account = fetch_account_by_id(self.conn, operation.account_id)
            invoice = fetch_invoice_by_id(self.conn, operation.invoice_id)
            self.tree.insert("", "end", values=(operation.income, operation.outcome, account.description, invoice.primary_reference if invoice else "", invoice.file_path if invoice else ""))

        # Add a row to display the total balance
        total_income, total_outcome = calculate_total_balance(self.conn)
        self.tree.insert("", "end", values=(total_income, total_outcome, "Total Balance", "", ""))

    def add_operation(self):
        # Open a dialog to enter operation details
        # Call insert_operation() with the new operation data
        self.populate_treeview()

    def edit_operation(self):
        # Retrieve the selected operation from the treeview
        selected = self.tree.focus()
        if selected:
            # Open a dialog to edit operation details
            # Call update_operation() with the updated operation data
            self.populate_treeview()

    def delete_operation(self):
        # Retrieve the selected operation from the treeview
        selected = self.tree.focus()
        if selected:
            # Call delete_operation() with the selected operation id
            self.populate_treeview()

    def open_file(self, event):
        # Retrieve the selected item from the treeview
        selected_item = self.tree.focus()
        if selected_item:
            # Get the file path from the selected item
            file_path = self.tree.set(selected_item, "file_path")
            if file_path:
                # Open the file
                open_file(file_path)


class InvoiceDialog(tk.Toplevel):
    def __init__(self, parent, title, invoice=None):
        super().__init__(parent)
        self.title(title)
        self.title_str = title
        self.result = None
        self.conn = parent.conn
        self.parent = parent
        self.invoice = invoice

        # Create UI elements to enter invoice details
        label_frame = tk.LabelFrame(self, text="Invoice Details")
        label_frame.pack(pady=10, padx=10)

        # Primary Receiver
        primary_receiver_label = tk.Label(label_frame, text="Primary Receiver:")
        primary_receiver_label.grid(row=0, column=0, sticky="w")
        self.primary_receiver_entry = tk.Entry(label_frame)
        self.primary_receiver_entry.grid(row=0, column=1)

        # Receiver Name
        receiver_name_label = tk.Label(label_frame, text="Receiver Name:")
        receiver_name_label.grid(row=1, column=0, sticky="w")
        self.receiver_name_entry = tk.Entry(label_frame)
        self.receiver_name_entry.grid(row=1, column=1)

        # Receiver Address
        receiver_address_label = tk.Label(label_frame, text="Receiver Address:")
        receiver_address_label.grid(row=2, column=0, sticky="w")
        self.receiver_address_entry = tk.Entry(label_frame)
        self.receiver_address_entry.grid(row=2, column=1)

        # Receiver Account
        receiver_account_label = tk.Label(label_frame, text="Receiver Account:")
        receiver_account_label.grid(row=3, column=0, sticky="w")
        self.receiver_account_entry = tk.Entry(label_frame)
        self.receiver_account_entry.grid(row=3, column=1)

        # Primary Reference
        primary_reference_label = tk.Label(label_frame, text="Primary Reference:")
        primary_reference_label.grid(row=4, column=0, sticky="w")
        self.primary_reference_entry = tk.Entry(label_frame)
        self.primary_reference_entry.grid(row=4, column=1)

        # Secondary Reference
        secondary_reference_label = tk.Label(label_frame, text="Secondary Reference:")
        secondary_reference_label.grid(row=5, column=0, sticky="w")
        self.secondary_reference_entry = tk.Entry(label_frame)
        self.secondary_reference_entry.grid(row=5, column=1)

        # Invoice Date
        invoice_date_label = tk.Label(label_frame, text="Invoice Date:")
        invoice_date_label.grid(row=6, column=0, sticky="w")
        self.invoice_date_entry = tk.Entry(label_frame)
        self.invoice_date_entry.grid(row=6, column=1)

        # Due Date
        due_date_label = tk.Label(label_frame, text="Due Date:")
        due_date_label.grid(row=7, column=0, sticky="w")
        self.due_date_entry = tk.Entry(label_frame)
        self.due_date_entry.grid(row=7, column=1)

        # Amount
        amount_label = tk.Label(label_frame, text="Amount:")
        amount_label.grid(row=8, column=0, sticky="w")
        self.amount_entry = tk.Entry(label_frame)
        self.amount_entry.grid(row=8, column=1)

        # Paying Account
        paying_account_label = tk.Label(label_frame, text="Paying Account:")
        paying_account_label.grid(row=9, column=0, sticky="w")
        self.paying_account_combo = ttk.Combobox(label_frame)
        self.paying_account_combo.grid(row=9, column=1)

        # Populate the paying account combo box
        accounts = fetch_accounts(self.conn)
        self.paying_account_combo["values"] = [account.description for account in accounts]

        # Remark
        remark_label = tk.Label(label_frame, text="Remark:")
        remark_label.grid(row=10, column=0, sticky="w")
        self.remark_entry = tk.Entry(label_frame)
        self.remark_entry.grid(row=10, column=1)

        # Description
        description_label = tk.Label(label_frame, text="Description:")
        description_label.grid(row=11, column=0, sticky="w")
        self.description_entry = tk.Entry(label_frame)
        self.description_entry.grid(row=11, column=1)

        # Note
        note_label = tk.Label(label_frame, text="Note:")
        note_label.grid(row=12, column=0, sticky="w")
        self.note_entry = tk.Entry(label_frame)
        self.note_entry.grid(row=12, column=1)

        # Tag
        tag_label = tk.Label(label_frame, text="Tag:")
        tag_label.grid(row=13, column=0, sticky="w")
        self.tag_entry = tk.Entry(label_frame)
        self.tag_entry.grid(row=13, column=1)

        # Category
        category_label = tk.Label(label_frame, text="Category:")
        category_label.grid(row=14, column=0, sticky="w")
        self.category_entry = tk.Entry(label_frame)
        self.category_entry.grid(row=14, column=1)

        # Add a button to open the file browser
        file_path_label = tk.Label(self, text="File Path:")
        file_path_label.pack()
        self.file_path_entry = tk.Entry(self)
        self.file_path_entry.pack()

        file_button = tk.Button(self, text="Select File", command=self.select_file)
        file_button.pack()

        # Add buttons to save or cancel
        save_button = tk.Button(self, text="Save", command=self.save)
        save_button.pack()

        cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        cancel_button.pack()

        # Populate the dialog with invoice data if editing
        if invoice:
            self.populate_fields(invoice)

    def select_file(self):
        file_path = tk.filedialog.askopenfilename()
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)

    def save(self):
        if not self.validate_fields():
            return

        id = self.invoice.id
        primary_receiver = self.primary_receiver_entry.get()
        receiver_name = self.receiver_name_entry.get()
        receiver_address = self.receiver_address_entry.get()
        receiver_account = self.receiver_account_entry.get()
        primary_reference = self.primary_reference_entry.get()
        secondary_reference = self.secondary_reference_entry.get()
        invoice_date = self.invoice_date_entry.get()
        due_date = self.due_date_entry.get()
        amount = float(self.amount_entry.get())
        paying_account_id = self.get_paying_account_id()
        file_path = self.file_path_entry.get()
        remark = self.remark_entry.get()
        description = self.description_entry.get()
        note = self.note_entry.get()
        tag = self.tag_entry.get()
        category = self.category_entry.get()

        invoice = Invoice(
            id = id,
            primary_receiver=primary_receiver,
            receiver_name=receiver_name,
            receiver_address=receiver_address,
            receiver_account=receiver_account,
            primary_reference=primary_reference,
            secondary_reference=secondary_reference,
            invoice_date=invoice_date,
            due_date=due_date,
            paid_date=None,
            amount=amount,
            paying_account_id=paying_account_id,
            file_path=file_path,
            remark=remark,
            description=description,
            note=note,
            tag=tag,
            category=category
        )

        self.result = invoice
        ttl = self.title_str
        print("self.title_str " + self.title_str)
        if self.result and self.title_str == "Add Invoice":
            insert_invoice(self.conn, self.result)
            self.parent.populate_treeview()
        elif self.result and self.title_str == "Edit Invoice":
            update_invoice(self.conn, self.result)
            self.parent.populate_treeview()
        self.destroy()


    def validate_fields(self):
        if not self.receiver_name_entry.get():
            tk.messagebox.showerror("Error", "Receiver name is required.")
            return False

        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid amount value.")
            return False

        if not self.paying_account_combo.get():
            tk.messagebox.showerror("Error", "Paying account is required.")
            return False

        return True

    def get_paying_account_id(self):
        account_description = self.paying_account_combo.get()
        for account in fetch_accounts(self.conn):
            if account.description == account_description:
                return account.id
        return None

    def populate_fields(self, invoice):
        self.primary_receiver_entry.insert(0, invoice.primary_receiver)
        self.receiver_name_entry.insert(0, invoice.receiver_name)
        self.receiver_address_entry.insert(0, invoice.receiver_address)
        self.receiver_account_entry.insert(0, invoice.receiver_account)
        self.primary_reference_entry.insert(0, invoice.primary_reference)
        self.secondary_reference_entry.insert(0, invoice.secondary_reference)
        self.invoice_date_entry.insert(0, invoice.invoice_date)
        self.due_date_entry.insert(0, invoice.due_date)
        self.amount_entry.insert(0, str(invoice.amount))
        self.paying_account_combo.set(self.get_account_description(invoice.paying_account_id))
        self.file_path_entry.insert(0, invoice.file_path)
        self.remark_entry.insert(0, invoice.remark)
        self.description_entry.insert(0, invoice.description)
        self.note_entry.insert(0, invoice.note)
        self.tag_entry.insert(0, invoice.tag)
        self.category_entry.insert(0, invoice.category)

    def get_account_description(self, account_id):
        for account in fetch_accounts(self.conn):
            if account.id == account_id:
                return account.description
        return None


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Invoices to Pay Manager")
        self.conn = sqlite3.connect("data/database.db", check_same_thread=False)


        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.invoices_to_pay_view = InvoicesToPayView(self.notebook, self.conn)
        self.notebook.add(self.invoices_to_pay_view, text="Invoices to Pay")

        self.accounts_view = AccountsView(self.notebook, self.conn)
        self.notebook.add(self.accounts_view, text="Accounts")

        self.operations_view = OperationsView(self.notebook, self.conn)
        self.notebook.add(self.operations_view, text="Operations")
        # Add a menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Backup Database", command=self.backup_database)
        file_menu.add_command(label="Restore Database", command=self.restore_database)

    def backup_database(self):
        backup_dir = filedialog.askdirectory(title="Select Backup Directory")
        if backup_dir:
            backup_database(self.conn, backup_dir)

    def restore_database(self):
        backup_file = filedialog.askopenfilename(title="Select Backup File", filetypes=[("SQLite Database", "*.db")])
        if backup_file:
            restore_database(self.conn, backup_file)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
