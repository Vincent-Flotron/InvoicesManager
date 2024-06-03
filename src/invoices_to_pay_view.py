import tkinter as tk
from tkinter import ttk
from datetime import datetime
from models import Invoice, Operation
import utils
from my_treeview import MyTreeview
import validation
import format


class InvoicesToPayView(tk.Frame):
    def __init__(self, parent, conn, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.conn = conn
        utils.create_tables(conn)
        self.parent = parent

        # Create UI elements
        self.tree = MyTreeview(self, columns=("id", "primary_receiver", "receiver_name", "receiver_address", "receiver_account", "primary_reference", "secondary_reference", "invoice_date", "due_date", "paid_date", "amount", "paying_account", "file_path", "remark", "description", "note", "tag", "category"), show="headings")
        self.tree.pack(side="top", fill="both", expand=True)

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

        # Populate the treeview
        self.populate_treeview()
        
        # Bind double-click event to open file
        self.tree.bind("<Double-1>", self.open_file)

    def populate_treeview(self, invoices=None):
        # Clear the treeview
        self.tree.delete(*self.tree.get_children())

        # Fetch invoices from the database or use provided invoices
        if invoices is None:
            invoices = utils.fetch_invoices(self.conn)

        # Insert invoices into the treeview
        for invoice in invoices:
            account = utils.fetch_account_by_id(self.conn, invoice.paying_account_id)
            acount_description = account.description if account != None else ""
            self.tree.insert("", "end", values=(invoice.id, invoice.primary_receiver, invoice.receiver_name,
                                                invoice.receiver_address, invoice.receiver_account, invoice.primary_reference,
                                                invoice.secondary_reference, invoice.invoice_date, invoice.due_date,
                                                invoice.paid_date, invoice.amount, acount_description, invoice.file_path,
                                                invoice.remark, invoice.description, invoice.note, invoice.tag, invoice.category))

    def add_invoice(self):
        # Open a dialog to enter invoice details
        dialog = InvoiceDialog(self, self.parent, title="Add Invoice")


    def edit_invoice(self):
        # Retrieve the selected invoice from the treeview
        selected = self.tree.focus()
        if selected:
            invoice_id = self.tree.item(selected)["values"][0]
            invoice = utils.fetch_invoice_by_id(self.conn, invoice_id)
            dialog = InvoiceDialog(self, self.parent, title="Edit Invoice", invoice=invoice)


    def delete_invoice(self):
        # Retrieve the selected invoice from the treeview
        selected = self.tree.focus()
        if selected:
            # Call delete_invoice() with the selected invoice id
            invoice_id = self.tree.item(selected)["values"][0]
            relative_operation = utils.fetch_operation_by_invoice_id(self.conn, invoice_id)
            if relative_operation == None:
                utils.delete_invoice(self.conn, invoice_id)
                self.populate_treeview()
            else:
                tk.messagebox.showinfo("Impossible to delete", f"The Operation with id '{relative_operation.id}' is linked to this invoice.\nPlease delete this operation before.")

    def filter_invoices(self):
        search_term = self.search_entry.get().lower()
        filtered_invoices = utils.filter_invoices(self.conn, search_term)
        self.populate_treeview(filtered_invoices)

    def open_file(self, event):
        # Retrieve the selected item from the treeview
        selected_item = self.tree.focus()
        if selected_item:
            # Get the file path from the selected item
            file_path = self.tree.set(selected_item, "file_path")
            if file_path:
                # Open the file
                utils.open_file(file_path)


class InvoiceDialog(tk.Toplevel):
    def __init__(self, parent, notebook, title, invoice=None):
        super().__init__(parent)
        self.title(title)
        self.title_str = title
        self.result = None
        self.conn = parent.conn
        self.parent = parent
        self.notebook = notebook
        self.id = invoice.id if invoice != None else None

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

        # Paid Date
        paid_date_label = tk.Label(label_frame, text="Paid Date:")
        paid_date_label.grid(row=8, column=0, sticky="w")
        self.paid_date_entry = tk.Entry(label_frame)
        self.paid_date_entry.grid(row=8, column=1)

        # Amount
        amount_label = tk.Label(label_frame, text="Amount:")
        amount_label.grid(row=9, column=0, sticky="w")
        self.amount_entry = tk.Entry(label_frame)
        self.amount_entry.grid(row=9, column=1)

        # Paying Account
        paying_account_label = tk.Label(label_frame, text="Paying Account:")
        paying_account_label.grid(row=10, column=0, sticky="w")
        self.paying_account_combo = ttk.Combobox(label_frame)
        self.paying_account_combo.grid(row=10, column=1)

        # Populate the paying account combo box
        accounts = utils.fetch_accounts(self.conn)
        self.paying_account_combo["values"] = [account.description for account in accounts]

        # Remark
        remark_label = tk.Label(label_frame, text="Remark:")
        remark_label.grid(row=11, column=0, sticky="w")
        self.remark_entry = tk.Entry(label_frame)
        self.remark_entry.grid(row=11, column=1)

        # Description
        description_label = tk.Label(label_frame, text="Description:")
        description_label.grid(row=12, column=0, sticky="w")
        self.description_entry = tk.Entry(label_frame)
        self.description_entry.grid(row=12, column=1)

        # Note
        note_label = tk.Label(label_frame, text="Note:")
        note_label.grid(row=13, column=0, sticky="w")
        self.note_entry = tk.Entry(label_frame)
        self.note_entry.grid(row=13, column=1)

        # Tag
        tag_label = tk.Label(label_frame, text="Tag:")
        tag_label.grid(row=14, column=0, sticky="w")
        self.tag_entry = tk.Entry(label_frame)
        self.tag_entry.grid(row=14, column=1)

        # Category
        category_label = tk.Label(label_frame, text="Category:")
        category_label.grid(row=15, column=0, sticky="w")
        self.category_entry = tk.Entry(label_frame)
        self.category_entry.grid(row=15, column=1)

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

        id = self.id
        primary_receiver = self.primary_receiver_entry.get()
        receiver_name = self.receiver_name_entry.get()
        receiver_address = self.receiver_address_entry.get()
        receiver_account = self.receiver_account_entry.get()
        primary_reference = self.primary_reference_entry.get()
        secondary_reference = self.secondary_reference_entry.get()
        invoice_date = self.invoice_date_entry.get()
        invoice_date = format.format_date(self.invoice_date_entry.get()) if invoice_date != '' else invoice_date
        due_date = self.due_date_entry.get()
        due_date = format.format_date(self.due_date_entry.get()) if due_date != '' else due_date
        paid_date = self.paid_date_entry.get()
        paid_date = format.format_date(self.paid_date_entry.get()) if paid_date != '' else paid_date
        amount = round(float(self.amount_entry.get()), 2)
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
            paid_date=paid_date,
            amount=amount,
            paying_account_id=paying_account_id,
            file_path=file_path,
            remark=remark,
            description=description,
            note=note,
            tag=tag,
            category=category
        )

        # self.result = invoice
        recorded_invoice = utils.fetch_invoice_by_id(self.conn, invoice.id)
        insert_new_operation = False
        if invoice and self.title_str == "Add Invoice":
            invoice.id = utils.insert_invoice(self.conn, invoice)
            self.parent.populate_treeview()
            # Create a new operation
            if invoice.as_paying_account()   \
               and invoice.is_paid():
                insert_new_operation = True
        elif invoice and self.title_str == "Edit Invoice":
            # update invoice
            utils.update_invoice(self.conn, invoice)
            self.parent.populate_treeview()

            # Update relative operation if exists
            related_operation_was_updated = self.update_related_operation(recorded_invoice, invoice)

            # Create a new operation
            if not related_operation_was_updated \
               and invoice.as_paying_account()   \
               and invoice.is_paid():
                insert_new_operation = True
        if insert_new_operation:
            operation = Operation(
                            type='invoice',
                            paid_date=invoice.paid_date,
                            income=0,
                            outcome=invoice.amount,
                            account_id=invoice.paying_account_id,
                            invoice_id=invoice.id
                        )
            utils.insert_operation(self.conn, operation)
        # Update operations view
        self.notebook.children["!operationsview"].populate_treeview()
        self.destroy()

    def update_related_operation(self, recorded_invoice, invoice):
        has_relative_operation = False
        account_is_changing = recorded_invoice.paying_account_id != invoice.paying_account_id
        amount_is_changing = recorded_invoice.amount != invoice.amount
        relative_operation = utils.fetch_operation_by_invoice_id(self.conn, invoice.id)
        if relative_operation:
            if account_is_changing and invoice.is_paid():
                utils.update_operation_account_from_invoice(self.conn, invoice)
            if amount_is_changing and invoice.is_paid():
                utils.update_operation_outcome_from_invoice(self.conn, invoice)
            has_relative_operation = True
        return has_relative_operation

    def validate_fields(self):
        if not self.primary_receiver_entry.get():
            tk.messagebox.showerror("Error", "Primary receiver name is required.")
            return False

        try:
            amount = float(self.amount_entry.get())
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid amount value.")
            return False

        paying_account = self.paying_account_combo.get()
        if not paying_account:
            tk.messagebox.showerror("Error", "Paying account is required.")
            return False

        if not self.get_paying_account_id():
            tk.messagebox.showerror("Error", f"Paying account '{paying_account}' doesn't exist.")
            return False
        
        paid_date = self.paid_date_entry.get()
        if paid_date and not validation.date_is_valid(paid_date):
            tk.messagebox.showerror("Error", f"paid_date '{paid_date}' is not on format YYYY.MM.DD or YY.M.D or YYYY-MM-DD or YY-M-D.")
            return False
        
        due_date = self.due_date_entry.get()
        if due_date and not validation.date_is_valid(due_date):
            tk.messagebox.showerror("Error", f"due_date '{due_date}' is not on format YYYY.MM.DD or YY.M.D or YYYY-MM-DD or YY-M-D.")
            return False

        invoice_date = self.invoice_date_entry.get()
        if invoice_date and not validation.date_is_valid(invoice_date):
            tk.messagebox.showerror("Error", f"invoice_date '{invoice_date}' is not on format YYYY.MM.DD or YY.M.D or YYYY-MM-DD or YY-M-D.")
            return False

        return True

    def get_paying_account_id(self):
        account_description = self.paying_account_combo.get()
        for account in utils.fetch_accounts(self.conn):
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
        self.paid_date_entry.insert(0, invoice.paid_date)
        self.amount_entry.insert(0, str(invoice.amount))
        self.paying_account_combo.set(self.get_account_description(invoice.paying_account_id))
        self.file_path_entry.insert(0, invoice.file_path)
        self.remark_entry.insert(0, invoice.remark)
        self.description_entry.insert(0, invoice.description)
        self.note_entry.insert(0, invoice.note)
        self.tag_entry.insert(0, invoice.tag)
        self.category_entry.insert(0, invoice.category)

    def get_account_description(self, account_id):
        for account in utils.fetch_accounts(self.conn):
            if account.id == account_id:
                return account.description
        return None