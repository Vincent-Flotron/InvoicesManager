import tkinter as tk
from datetime import datetime
from models import Account
import utils
from my_treeview import MyTreeview


class AccountsView(tk.Frame):
    def __init__(self, parent, conn, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.conn = conn

        # Create UI elements
        self.tree = MyTreeview(self, columns=("id", "description", "bank_name", "account_number"), show="headings")
        self.tree.pack(side="top", fill="both", expand=True)

        # Configure columns
        self.tree.heading("id", text="ID")
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
        accounts = utils.fetch_accounts(self.conn)

        # Insert accounts into the treeview
        for account in accounts:
            self.tree.insert("", "end", values=(account.id, account.description, account.bank_name, account.account_number))

    def add_account(self):
        # Open a dialog to enter account details
        dialog = AccountDialog(self, title="Add Account")

    def edit_account(self):
        # Retrieve the selected account from the treeview
        selected = self.tree.focus()
        if selected:
            account_id = self.tree.item(selected)["values"][0]
            account = utils.fetch_account_by_id(self.conn, account_id)
            dialog = AccountDialog(self, title="Edit Account", account=account)

    def delete_account(self):
        # Retrieve the selected account from the treeview
        selected = self.tree.focus()
        if selected:
            account_id = self.tree.item(selected)["values"][0]
            utils.delete_account(self.conn, account_id)
            self.populate_treeview()


class AccountDialog(tk.Toplevel):
    def __init__(self, parent, title, account=None):
        super().__init__(parent)
        self.title(title)
        self.title_str = title
        self.parent = parent
        self.result = None
        self.conn = parent.conn
        self.id = account.id if account != None else None

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
        if account:
            self.populate_fields(account)

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
        if self.result and self.title_str == "Add Account":
            utils.insert_account(self.conn, self.result)
            self.parent.populate_treeview()
        elif self.result and self.title_str == "Edit Account":
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
