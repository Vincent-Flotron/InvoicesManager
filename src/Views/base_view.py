import tkinter as tk
from tkinter import ttk
from datetime import datetime
from models import Invoice, Operation, Account
import utils
from my_treeview import MyTreeview
import validation
import format

class BaseView(tk.Frame):
    def __init__(self, parent, conn, view_name, columns, columns_names, dialog_class, delete_func, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.conn = conn
        self.parent = parent
        self.view_name = view_name
        self.columns = columns
        self.columns_names = columns_names
        self.dialog_class = dialog_class
        self.delete_func = delete_func

        # Create UI elements
        self.tree = MyTreeview(self, columns=columns, show="headings")
        self.tree.pack(side="top", fill="both", expand=True)

        # Configure columns
        for col, col_name in zip(columns, columns_names):
            self.tree.heading(col, text=col_name.replace("_", " ").capitalize())

        # Add buttons
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x")

        add_button = tk.Button(button_frame, text="Add", command=self.add_item)
        add_button.pack(side="left")

        edit_button = tk.Button(button_frame, text="Edit", command=self.edit_item)
        edit_button.pack(side="left")

        delete_button = tk.Button(button_frame, text="Delete", command=self.delete_items)
        delete_button.pack(side="left")

        # Add a search entry and filter button
        if self.view_name == "operations_view":
            search_frame = tk.Frame(self)
            search_frame.pack(side="top", fill="x")

            self.search_entry = tk.Entry(search_frame)
            self.search_entry.pack(side="left", fill="x", expand=True)

            filter_button = tk.Button(search_frame, text="Filter", command=self.filter_items)
            filter_button.pack(side="operations", text="Add Customized Account Closure", command=self.add_customized_account_closure)
            customized_closure_button.pack(side="left")

        # Label to display the sum or total balance of selected items
        if self.view_name == "invoices_to_pay":
            self.sum_label = tk.Label(self, text="Sum of selected invoices: 0.00")
            self.sum_label.pack(side="top", fill="x")
        elif self.view_name == "operations":
            self.total_balance_label = tk.Label(self, text="Total Balance: 0.00")
            self.total_balance_label.pack(side="top", fill="x")

        # Populate the treeview
        self.update_view()

        # Bind events
        self.tree.bind("<Double-1>", self.open_file)
        self.tree.bind("<<TreeviewSelect>>", self.update_sum_or_total_balance)

    def populate_treeview(self, view_name):
        # Clear the treeview
        self.tree.delete(*self.tree.get_children())

        # Fetch items from the database
        if   view_name == "invoices_to_pay":
            selected_items = utils.fetch_invoices(self.conn)
        elif view_name == "operations":
            selected_items = utils.fetch_operations(self.conn)
        elif view_name == "accounts":
            selected_items = utils.fetch_accounts(self.conn)

        self.insert_rows(selected_items)

    def update_view(self):
        self.populate_treeview(self.view_name)

    def update_operations(self):
        self.populate_treeview("operations")

    def update_accounts(self):
        self.populate_treeview("accounts")

    def insert_rows(self, selected_items):
        # Insert items into the treeview
        remain = 0
        for sel_item in selected_items:
            values = [getattr(sel_item, col) if hasattr(sel_item, col) else '' for col in self.columns]
            if self.view_name == "operations" and sel_item.invoice_id:
                invoice = utils.fetch_invoice_by_id(self.conn, sel_item.invoice_id)
                missing_invoices_mess = None
                missing_account_mess  = None
                if not invoice:
                    missing_invoices_mess = f"The operation with id '{sel_item.id}' has as a deleted invoice reference. invoice ref id: '{sel_item.invoice_id}'"
                account = utils.fetch_account_by_id(self.conn, sel_item.account_id)
                if not account:
                    missing_account_mess = f"The operation with id '{sel_item.id}' has as a deleted account reference. account ref id: '{sel_item.account_id}'"
                values[5]     = remain = remain + values[3] - values[4]
                values[6]     = account.description if not missing_account_mess else missing_account_mess
                if not missing_invoices_mess:
                    values[7] = invoice.primary_receiver
                    values[8] = invoice.primary_reference
                    values[9] = invoice.file_path
                else:
                    values[7] = missing_invoices_mess
                    values[8] = missing_invoices_mess
                    values[9] = missing_invoices_mess
            self.tree.insert("", "end", values=values)

        # Add a row to display the total balance for the operations view
        if self.view_name == "operations":
            total_income  = sum(item.income  for item in selected_items if item.income  is not None)
            total_outcome = sum(item.outcome for item in selected_items if item.outcome is not None)
            total_balance = total_income - total_outcome
            self.tree.insert("", "end", values=("Total", "", "", f"{total_income:.2f}", f"{total_outcome:.2f}", "", "", f"{total_balance:.2f}"))

    def add_checkboxes_filter(self, filter_on="account", record_to_thick_list=["true", "false"], text_attribute="description", variable_attribute="id", item_linked_attribute="account_id"):
        # Keep for method filter_operations
        self.variable_attribute = variable_attribute
        self.item_linked_attribute = item_linked_attribute

        # Add a frame for the filter options
        filter_frame = tk.Frame(self)
        filter_frame.pack(side="top", fill="x")

        # Add a label for the filter options
        filter_label = tk.Label(filter_frame, text=f"Filter by {filter_on}:")
        filter_label.pack(side="left")

        # Add a Checkbutton for each account
        self.checkbox_vars = {}
        text = ''
        variable = ''
        for i, record_to_thick in enumerate(record_to_thick_list):
            self.checkbox_vars[getattr(record_to_thick, variable_attribute)] = tk.BooleanVar(value=True)
            if(type(record_to_thick_list[0]) != str):
                text = getattr(record_to_thick, text_attribute)
                variable = self.checkbox_vars[getattr(record_to_thick, variable_attribute)]
            else:
                text = record_to_thick
                variable = record_to_thick
            account_checkbutton = tk.Checkbutton(filter_frame, text=text, variable=variable, command=self.filter_operations)
            account_checkbutton.pack(side="left")

    def filter_operations(self):
        # Clear the treeview
        self.tree.delete(*self.tree.get_children())

        # Fetch items from the database
        if self.view_name   == "invoices_to_pay":
            selected_items   = utils.fetch_invoices(self.conn)
        elif self.view_name == "operations":
            selected_items   = utils.fetch_operations(self.conn)
        elif self.view_name == "accounts":
            selected_items   = utils.fetch_accounts(self.conn)

        # Filter operations based on selected accounts
        selected_items_on_filter = [text for text, var in self.checkbox_vars.items() if var.get()]
        filtered_items = [item for item in selected_items if getattr(item, self.item_linked_attribute) in selected_items_on_filter]

        # Insert the filtered operations into the treeview
        self.insert_rows(filtered_items)

        # Update the totals
        self.update_sum_or_total_balance(None)

    def add_item(self):
        # Open a dialog to enter item details
        dialog = self.dialog_class(self, self.parent, title="Add_Item")

    def edit_item(self):
        # Retrieve the selected item from the treeview
        selected = self.tree.focus()
        selected_items = self.tree.selection()
        if selected_items:
            item_ids = []
            for item in selected_items:
                item_id = self.tree.item(item)["values"][0]
                item_ids.append(item_id)
            if self.view_name == "invoices_to_pay":
                items = utils.fetch_invoices_by_ids(self.conn, item_ids)
            elif self.view_name == "operations":
                items = utils.fetch_operations_by_ids(self.conn, item_ids)
            elif self.view_name == "accounts":
                items = utils.fetch_accounts_by_ids(self.conn, item_ids)
            dialog = self.dialog_class(self, self.parent, title="Edit_Item", selected_items=items)
            if dialog.need_update_view and self.view_name   == "invoices_to_pay":
                # Re-populate the treeviews
                self.update_operations()
                self.update_view()
            elif dialog.need_update_view and self.view_name == "accounts":
                # Re-populate the treeviews
                self.update_accounts()
                self.update_view()
            elif dialog.need_update_view:
                # Re-populate the treeview
                self.update_view()


    def delete_items(self):
        # Retrieve the selected items from the treeview
        selected_items = self.tree.selection()
        if selected_items:
            # Iterate through the selected items and delete them from the database
            for item in selected_items:
                item_id = self.tree.item(item)["values"][0]
                self.delete_func(self.conn, item_id)
            # Re-populate the treeview
            self.update_view()

    def filter_items(self):
        # Get the search term from the entry widget
        search_term = self.search_entry.get().lower()

        # Clear the treeview
        self.tree.delete(*self.tree.get_children())

        # Fetch items from the database
        items = utils.fetch_invoices(self.conn)

        # Filter items based on the search term
        filtered_items = [item for item in items if search_term in item.primary_receiver.lower() or search_term in item.receiver_name.lower() or search_term in item.primary_reference.lower()]

        # Insert items into the treeview
        for item in filtered_items:
            values = [getattr(item, col) for col in self.columns]
            self.tree.insert("", "end", values=values)

    def open_file(self, event):
        # Retrieve the selected item from the treeview
        selected_item = self.tree.focus()
        if selected_item:
            # Get the file path from the selected item
            file_path = self.tree.set(selected_item, "file_path")
            if file_path:
                # Open the file
                utils.open_file(file_path)

    def update_sum_or_total_balance(self, event):
        selected_items = self.tree.selection()
        if self.view_name == "invoices_to_pay":
            # Calculate the sum of the selected invoices
            total_sum = 0.0
            for item in selected_items:
                total_sum += float(self.tree.item(item, "values")[10]) or 0.0
            self.sum_label.config(text=f"Sum of selected invoices: {total_sum:.2f}")
        elif self.view_name == "operations":
            # Calculate the total balance of the selected operations
            total_income = 0.0
            total_outcome = 0.0
            for item in selected_items:
                total_income += float(self.tree.item(item, "values")[3]) or 0.0
                total_outcome += float(self.tree.item(item, "values")[4]) or 0.0
            total_balance = total_income - total_outcome
            self.total_balance_label.config(text=f"Total Balance: {total_balance:.2f}")
