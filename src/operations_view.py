import tkinter as tk
from tkinter import ttk
from datetime import datetime
from models import Operation
import utils
from my_treeview import MyTreeview

class OperationsView(tk.Frame):
    def __init__(self, parent, conn, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.conn = conn

        # Create UI elements
        self.tree = MyTreeview(self, columns=("id", "income", "outcome", "account", "invoice", "file_path"), show="headings")
        self.tree.pack(side="top", fill="both", expand=True)

        # Configure columns
        self.tree.heading("id", text="ID")
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
        operations = utils.fetch_operations(self.conn)

        # Insert operations into the treeview
        for operation in operations:
            account = utils.fetch_account_by_id(self.conn, operation.account_id)
            invoice = utils.fetch_invoice_by_id(self.conn, operation.invoice_id)
            self.tree.insert("", "end", values=(operation.id, operation.income, operation.outcome, account.description if account else "", invoice.primary_reference if invoice else "", invoice.file_path if invoice else ""))

        # Add a row to display the total balance
        total_income, total_outcome = utils.calculate_total_balance(self.conn)
        self.tree.insert("", "end", values=("", total_income, total_outcome, "Total Balance", "", ""))

    def add_operation(self):
        # Open a dialog to enter operation details
        dialog = OperationDialog(self, title="Add Operation")

    def edit_operation(self):
        # Retrieve the selected operation from the treeview
        selected = self.tree.focus()
        if selected:
            operation_id = self.tree.item(selected)["values"][0]
            operation = utils.fetch_operation_by_id(self.conn, operation_id)
            dialog = OperationDialog(self, title="Edit Operation", operation=operation)
            if dialog.result:
                utils.update_operation(self.conn, dialog.result)
                self.populate_treeview()

    def delete_operation(self):
        # Retrieve the selected operation from the treeview
        selected = self.tree.focus()
        if selected:
            operation_id = self.tree.item(selected)["values"][0]
            utils.delete_operation(self.conn, operation_id)
            self.populate_treeview()

    def open_file(self, event):
        # Retrieve the selected item from the treeview
        selected_item = self.tree.focus()
        if selected_item:
            # Get the file path from the selected item
            file_path = self.tree.set(selected_item, "file_path")
            if file_path:
                # Open the file
                utils.open_file(file_path)


class OperationDialog(tk.Toplevel):
    def __init__(self, parent, title, operation=None):
        super().__init__(parent)
        self.title(title)
        self.title_str = title
        self.parent = parent
        self.result = None
        self.conn = parent.conn
        self.id = operation.id if operation != None else None

        # Create UI elements to enter operation details
        label_frame = tk.LabelFrame(self, text="Operation Details")
        label_frame.pack(pady=10, padx=10)

        # Income
        income_label = tk.Label(label_frame, text="Income:")
        income_label.grid(row=0, column=0, sticky="w")
        self.income_entry = tk.Entry(label_frame)
        self.income_entry.grid(row=0, column=1)

        # Outcome
        outcome_label = tk.Label(label_frame, text="Outcome:")
        outcome_label.grid(row=1, column=0, sticky="w")
        self.outcome_entry = tk.Entry(label_frame)
        self.outcome_entry.grid(row=1, column=1)

        # Account
        account_label = tk.Label(label_frame, text="Account:")
        account_label.grid(row=2, column=0, sticky="w")
        self.account_combo = ttk.Combobox(label_frame)
        self.account_combo.grid(row=2, column=1)

        # Populate the account combo box
        accounts = utils.fetch_accounts(self.conn)
        self.account_combo["values"] = [account.description for account in accounts]

        # Invoice
        invoice_label = tk.Label(label_frame, text="Invoice:")
        invoice_label.grid(row=3, column=0, sticky="w")
        self.invoice_combo = ttk.Combobox(label_frame)
        self.invoice_combo.grid(row=3, column=1)

        # Populate the invoice combo box
        invoices = utils.fetch_invoices(self.conn)
        self.invoice_combo["values"] = [invoice.primary_reference for invoice in invoices]

        # Add buttons to save or cancel
        save_button = tk.Button(self, text="Save", command=self.save)
        save_button.pack()

        cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        cancel_button.pack()

        # Populate the dialog with operation data if editing
        if operation:
            self.populate_fields(operation)

    def save(self):
        if not self.validate_fields():
            return

        id = self.id
        income = float(self.income_entry.get())
        outcome = float(self.outcome_entry.get())
        account_id = self.get_account_id()
        invoice_id = self.get_invoice_id()

        operation = Operation(
            id=id,
            income=income,
            outcome=outcome,
            account_id=account_id,
            invoice_id=invoice_id
        )

        self.result = operation
        ttl = self.title_str
        print("self.title_str " + self.title_str)
        if self.result and self.title_str == "Add Operation":
            utils.insert_operation(self.conn, self.result)
            self.parent.populate_treeview()
        elif self.result and self.title_str == "Edit Operation":
            utils.update_operation(self.conn, self.result)
            self.parent.populate_treeview()
        self.destroy()

    def validate_fields(self):
        try:
            income = float(self.income_entry.get())
            outcome = float(self.outcome_entry.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid income or outcome value.")
            return False

        if not self.account_combo.get():
            tk.messagebox.showerror("Error", "Account is required.")
            return False

        return True

    def get_account_id(self):
        account_description = self.account_combo.get()
        for account in utils.fetch_accounts(self.conn):
            if account.description == account_description:
                return account.id
        return None

    def get_invoice_id(self):
        invoice_reference = self.invoice_combo.get()
        for invoice in utils.fetch_invoices(self.conn):
            if invoice.primary_reference == invoice_reference:
                return invoice.id
        return None

    def populate_fields(self, operation):
        self.income_entry.insert(0, str(operation.income))
        self.outcome_entry.insert(0, str(operation.outcome))
        self.account_combo.set(self.get_account_description(operation.account_id))
        self.invoice_combo.set(self.get_invoice_reference(operation.invoice_id))

    def get_account_description(self, account_id):
        for account in utils.fetch_accounts(self.conn):
            if account.id == account_id:
                return account.description
        return None

    def get_invoice_reference(self, invoice_id):
        for invoice in utils.fetch_invoices(self.conn):
            if invoice.id == invoice_id:
                return invoice.primary_reference
        return None