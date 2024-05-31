import tkinter as tk
from tkinter import ttk, filedialog
import sqlite3
import utils
from operations_view import OperationsView
from accounts_view import AccountsView
from invoices_to_pay_view import InvoicesToPayView
import os


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Invoices to Pay Manager")

        # Get the directory path of the current script
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.absolute_db_path = os.path.join(self.script_dir + "/..", "data/database.db")
        self.conn = sqlite3.connect(self.absolute_db_path, check_same_thread=False)

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
            utils.backup_database(self.conn, backup_dir, self.absolute_db_path)

    def restore_database(self):
        backup_file = filedialog.askopenfilename(title="Select Backup File", filetypes=[("SQLite Database", "*.db")])
        if backup_file:
            utils.restore_database(self.conn, backup_file, self.absolute_db_path)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
