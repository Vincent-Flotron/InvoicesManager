import tkinter as tk
from datetime import datetime
from models import Account
import utils
from base_view import BaseView


class AccountsView(BaseView):
    def __init__(self, parent, conn, *args, **kwargs):
        fields_for_columns = ("id", "description", "bank_name", "iban")
        dialog_class = AccountDialog
        delete_func = utils.delete_account
        columns_names = fields_for_columns
        super().__init__(parent, conn, "accounts", fields_for_columns, columns_names, dialog_class, delete_func, *args, **kwargs)

    def populate_treeview(self):
        # Clear the treeview
        self.tree.delete(*self.tree.get_children())

        # Fetch accounts from the database
        accounts = utils.fetch_accounts(self.conn)

        # Insert accounts into the treeview
        for account in accounts:
            self.tree.insert("", "end", values=(account.id, account.description, account.bank_name, account.iban))

class AccountDialog(tk.Toplevel):
    def __init__(self, parent, notebook, title, item=None):
        super().__init__(parent)
        self.title(title)
        self.title_str = title
        self.parent = parent
        self.notebook = notebook
        self.result = None
        self.conn = parent.conn
        self.id = item.id if item != None else None

        # Create UI elements to enter account details
        label_frame = tk.LabelFrame(self, text="Account Details")
        label_frame.pack(pady=10, padx=10)

        # Description
        description_label = tk.Label(label_frame, text="Description:")
        description_label.grid(row=0, column=0, sticky="w")
        self.description_entry = tk.Entry(label_frame)
        self.description_entry.grid(row=0, column=1)

        # Bank Name
        bank_name_label = tk.Label(label_frame, text="Bank Name:")
        bank_name_label.grid(row=1, column=0, sticky="w")
        self.bank_name_entry = tk.Entry(label_frame)
        self.bank_name_entry.grid(row=1, column=1)

        # Account Number
        account_number_label = tk.Label(label_frame, text="Account Number:")
        account_number_label.grid(row=2, column=0, sticky="w")
        self.account_number_entry = tk.Entry(label_frame)
        self.account_number_entry.grid(row=2, column=1)

        # Add buttons to save or cancel
        save_button = tk.Button(self, text="Save", command=self.save)
        save_button.pack()

        cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        cancel_button.pack()

        # Populate the dialog with account data if editing
        if item:
            self.populate_fields(item)

    def save(self):
        if not self.validate_fields():
            return


        id = self.id
        description = self.description_entry.get()
        bank_name = self.bank_name_entry.get()
        account_number = self.account_number_entry.get()

        account = Account(
            id=id,
            description=description,
            bank_name=bank_name,
            account_number=account_number
        )

        self.result = account
        ttl = self.title_str
        print("self.title_str " + self.title_str)
        if self.result and self.title_str == "Add_Item":
            utils.insert_account(self.conn, self.result)
            self.parent.populate_treeview()
        elif self.result and self.title_str == "Edit_Item":
            utils.update_account(self.conn, self.result)
            self.parent.populate_treeview()
        self.destroy()

    def validate_fields(self):
        if not self.description_entry.get():
            tk.messagebox.showerror("Error", "Description is required.")
            return False

        if not self.bank_name_entry.get():
            tk.messagebox.showerror("Error", "Bank name is required.")
            return False

        if not self.account_number_entry.get():
            tk.messagebox.showerror("Error", "Account number is required.")
            return False

        return True

    def populate_fields(self, account):
        self.description_entry.insert(0, account.description)
        self.bank_name_entry.insert(0, account.bank_name)
        self.account_number_entry.insert(0, account.account_number)
