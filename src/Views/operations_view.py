import tkinter as tk
from   tkinter         import ttk
from   datetime        import datetime
from   models          import Operation
from   tkinter         import font
from   Views.base_view import BaseView
import format
import utils
import validation


class OperationsView(BaseView):
    def __init__(self, parent, conn, *args, **kwargs):
        fields_for_columns = ("id", "paid_date", "type", "income", "outcome", "remain", "account_id", "receiver", "invoice_id", "file_path")
        dialog_class = OperationDialog
        delete_func = utils.delete_operation
        columns_names = ("id", "paid_date", "type", "income", "outcome", "remain", "account name", "receiver", "invoice ref", "file_path")
        super().__init__(parent, conn, "operations", fields_for_columns, columns_names, dialog_class, delete_func, *args, **kwargs)
        # self.auto_adjust_column_widths()

    # def auto_adjust_column_widths(self):
    #     for col in self.tree["columns"]:
    #         max_width = font.Font().measure(col.title())
    #         for item in self.tree.get_children():
    #             print(f'self.tree["columns"].index(col): {self.tree["columns"].index(col)}')
    #             print(f'self.tree.item(item)["values"]: {self.tree.item(item)["values"]}')
    #             print('-------')
    #             item_text = self.tree.item(item)["values"][self.tree["columns"].index(col)]
    #             max_width = max(max_width, font.Font().measure(str(item_text)))
    #         self.tree.column(col, width=max_width)

        super().add_checkboxes_filter(filter_on="account",
                                    record_to_thick_list=utils.fetch_accounts(self.conn),
                                    text_attribute="description",
                                    variable_attribute="id",
                                    item_linked_attribute="account_id")


    def add_customized_account_closure(self):
        selected = self.tree.focus()
        if not selected:
            tk.messagebox.showerror("Error", "No operation selected.")
            return

        selected_accounts = [desc for desc, var in self.checkbox_vars.items() if var.get()]
        if not selected_accounts:
            tk.messagebox.showerror("Error", "No account selected.")
            return

        total_income = 0
        total_outcome = 0

        # Fetch operations from the database
        operations = utils.fetch_operations(self.conn)

        # Filter operations based on selected accounts
        filtered_operations = [op for op in operations if utils.fetch_account_by_id(self.conn, op.account_id).description in selected_accounts]

        # Find the last customized_account_closure or starting_amount operation
        for account in selected_accounts:
            last_closure_operations = [op for op in filtered_operations if op.type == 'customized_account_closure' and utils.fetch_account_by_id(self.conn, op.account_id).description == account]
            last_starting_operations = [op for op in filtered_operations if op.type == 'starting_amount' and utils.fetch_account_by_id(self.conn, op.account_id).description == account]

            if last_closure_operations:
                last_operation = last_closure_operations[-1]
                total_income += sum(op.income for op in last_closure_operations)
                total_outcome += sum(op.outcome for op in last_closure_operations)
            elif last_starting_operations:
                last_operation = last_starting_operations[-1]
                total_income += sum(op.income for op in last_starting_operations)
                total_outcome += sum(op.outcome for op in last_starting_operations)

        new_operation = Operation(
            id=None,  # Assuming ID is auto-incremented
            paid_date=datetime.now().strftime("%Y-%m-%d"),
            income=total_income,
            outcome=total_outcome,
            account_id=utils.fetch_account_by_description(self.conn, selected_accounts[0]).id,
            invoice_id=None,
            type='customized_account_closure'
        )

        utils.insert_operation(self.conn, new_operation)
        self.populate_treeview()

class OperationDialog(tk.Toplevel):
    def __init__(self, parent, notebook, title, item=None):
        super().__init__(parent)
        self.title(title)
        self.title_str = title
        self.result = None
        self.conn = parent.conn
        self.parent = parent
        self.notebook = notebook
        self.id = item.id if item != None else None

        # Create UI elements to enter operation details
        label_frame = tk.LabelFrame(self, text="Operation Details")
        label_frame.pack(pady=10, padx=10)

        # Paid date
        paid_date_label = tk.Label(label_frame, text="Paid date:")
        paid_date_label.grid(row=0, column=0, sticky="w")
        self.paid_date_entry = tk.Entry(label_frame)
        self.paid_date_entry.grid(row=0, column=1)

        # Type
        type_label = tk.Label(label_frame, text="Type:")
        type_label.grid(row=1, column=0, sticky="w")
        self.type_entry = tk.Entry(label_frame)
        self.type_entry.grid(row=1, column=1)

        # Income
        income_label = tk.Label(label_frame, text="Income:")
        income_label.grid(row=2, column=0, sticky="w")
        self.income_entry = tk.Entry(label_frame)
        self.income_entry.grid(row=2, column=1)

        # Outcome
        outcome_label = tk.Label(label_frame, text="Outcome:")
        outcome_label.grid(row=3, column=0, sticky="w")
        self.outcome_entry = tk.Entry(label_frame)
        self.outcome_entry.grid(row=3, column=1)

        # Account
        account_label = tk.Label(label_frame, text="Account:")
        account_label.grid(row=4, column=0, sticky="w")
        self.account_combo = ttk.Combobox(label_frame)
        self.account_combo.grid(row=4, column=1)

        # Populate the account combo box
        accounts = utils.fetch_accounts(self.conn)
        self.account_combo["values"] = [account.description for account in accounts]

        # Invoice
        invoice_label = tk.Label(label_frame, text="Invoice:")
        invoice_label.grid(row=5, column=0, sticky="w")
        self.invoice_combo = ttk.Combobox(label_frame)
        self.invoice_combo.grid(row=5, column=1)

        # Populate the invoice combo box
        invoices = utils.fetch_invoices(self.conn)
        self.invoice_combo["values"] = [invoice.primary_reference for invoice in invoices]

        # Add buttons to save or cancel
        save_button = tk.Button(self, text="Save", command=self.save)
        save_button.pack()

        cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        cancel_button.pack()

        # Populate the dialog with operation data if editing
        if item:
            self.populate_fields(item)

    def save(self):
        if not self.validate_fields():
            return

        id = self.id
        paid_date = format.format_date(self.paid_date_entry.get())
        income = float(self.income_entry.get())
        outcome = float(self.outcome_entry.get())
        account_id = self.get_account_id()
        invoice_id = self.get_invoice_id()
        op_type = self.type_entry.get()

        operation = Operation(
            id=id,
            paid_date=paid_date,
            income=round(income, 2),
            outcome=round(outcome, 2),
            account_id=account_id,
            invoice_id=invoice_id,
            type=op_type
        )

        self.result = operation
        if self.result and self.title_str == "Add_Item":
            utils.insert_operation(self.conn, self.result)
            self.parent.populate_treeview()
        elif self.result and self.title_str == "Edit_Item":
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
        
        paid_date = self.paid_date_entry.get()
        if not validation.date_is_valid(paid_date):
            tk.messagebox.showerror("Error", f"paid_date '{paid_date}' is not on format YYYY.MM.DD or YY.MM.DD or YYYY-MM-DD or YY-MM-DD.")
            return False
        
        op_type = self.type_entry.get()
        if not validation.operation_type_is_valid(op_type):
            tk.messagebox.showerror("Error", f"type '{op_type}' is not on in the allowed types list: {Operation.op_types}")
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
        self.paid_date_entry.insert(0, operation.paid_date)
        self.type_entry.insert(0, operation.type)
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

