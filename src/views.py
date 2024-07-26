import tkinter as tk
from tkinter import ttk, filedialog
import utils
from Views.operations_view import OperationsView
from Views.accounts_view import AccountsView
from Views.invoices_to_pay_view import InvoicesToPayView


class MainApp(tk.Tk):
    def __init__(self, conn, absolute_db_path):
        super().__init__()
        self.title("Invoices to Pay Manager")

        self.absolute_db_path = absolute_db_path
        self.conn             = conn

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

