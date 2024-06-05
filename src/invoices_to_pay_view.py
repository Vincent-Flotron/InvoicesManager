import tkinter as tk
from tkinter import ttk
from models import Invoice, Operation
import utils
import validation
import format
from base_view import BaseView
from entry_label import EntryLabel

class InvoicesToPayView(BaseView):
    def __init__(self, parent, conn, *args, **kwargs):
        fields_for_columns = ("id", "primary_receiver", "receiver_name", "receiver_address", "receiver_account", "primary_reference", "secondary_reference", "invoice_date", "due_date", "paid_date", "amount", "file_path")
        dialog_class = InvoiceDialog
        delete_func = utils.delete_invoice
        columns_names = fields_for_columns
        super().__init__(parent, conn, "invoices_to_pay", fields_for_columns, columns_names, dialog_class, delete_func, *args, **kwargs)

class InvoiceDialog(tk.Toplevel):
    def __init__(self, parent, notebook, title, item=None):
        super().__init__(parent)
        self.title(title)
        self.title_str   = title
        self.result      = None
        self.conn        = parent.conn
        self.parent      = parent
        self.notebook    = notebook
        self.many_items  = type(item) is list
        self.id          = item.id if item != None else None

        # Create UI elements to enter invoice details
        label_frame = tk.LabelFrame(self, text="Invoice Details")
        label_frame.pack(pady=10, padx=10)
        self.entries_labels = EntryLabel(label_frame, self.many_items)

        # Primary Receiver
        self.entries_labels.make_entry_label("Primary Receiver", "primary_receiver")

        # Receiver Name
        self.entries_labels.make_entry_label("Receiver Name", "receiver_name")

        # Receiver Address
        self.entries_labels.make_entry_label("Receiver Address", "receiver_address")

        # Receiver Account
        self.entries_labels.make_entry_label("Receiver Account", "receiver_account")

        # Primary Reference
        self.entries_labels.make_entry_label("Primary Reference", "primary_reference")

        # Secondary Reference
        self.entries_labels.make_entry_label("Secondary Reference", "secondary_reference")

        # Invoice Date
        self.entries_labels.make_entry_label("Invoice Date", "invoice_date")

        # Due Date
        self.entries_labels.make_entry_label("Due Date", "due_date")

        # Paid Date
        self.entries_labels.make_entry_label("Paid Date", "paid_date")

        # Amount
        self.entries_labels.make_entry_label("Amount", "amount")

        # Paying Account
        self.entries_labels.make_entry_label("Paying Account", "paying_account", ttk.Combobox)

        # Populate the paying account combo box
        accounts = utils.fetch_accounts(self.conn)
        self.entries_labels.entries["paying_account"]["values"] = [account.description for account in accounts]

        # Remark
        self.entries_labels.make_entry_label("Remark", "remark")

        # Description
        self.entries_labels.make_entry_label("Description", "description")

        # Note
        self.entries_labels.make_entry_label("Note", "note")

        # Tag
        self.entries_labels.make_entry_label("Tag", "tag")

        # Category
        self.entries_labels.make_entry_label("Category", "category")

        # Add a button to open the file browser
        self.entries_labels.make_entry_label("File Path", "file_path")

        file_button = tk.Button(self, text="Select File", command=self.select_file)
        file_button.pack()

        # Add buttons to save or cancel
        save_button = tk.Button(self, text="Save", command=self.save)
        save_button.pack()

        cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        cancel_button.pack()

        # Populate the dialog with invoice data if editing
        if item:
            self.populate_fields(item)

    def select_file(self):
        file_path = tk.filedialog.askopenfilename()
        if file_path:
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)

    def save(self):
        if not self.validate_fields():
            return

        id                  = self.id
        primary_receiver    = self.entries_labels.entries['primary_receiver'].get()
        receiver_name       = self.entries_labels.entries['receiver_name'].get()
        receiver_address    = self.entries_labels.entries['receiver_address'].get()
        receiver_account    = self.entries_labels.entries['receiver_account'].get()
        primary_reference   = self.entries_labels.entries['primary_reference'].get()
        secondary_reference = self.entries_labels.entries['secondary_reference'].get()
        invoice_date        = self.entries_labels.entries['invoice_date'].get()
        invoice_date        =  format.format_date(self.entries_labels.entries['invoice_date'].get()) if invoice_date != '' else invoice_date
        due_date            = self.entries_labels.entries['due_date'].get()
        due_date            =  format.format_date(self.entries_labels.entries['due_date'].get()) if due_date != '' else due_date
        paid_date           = self.entries_labels.entries['paid_date'].get()
        paid_date           =  format.format_date(self.entries_labels.entries['paid_date'].get()) if paid_date != '' else paid_date
        amount              = round(float(self.entries_labels.entries['amount'].get()), 2)
        paying_account_id   = self.get_paying_account_id()
        file_path           = self.entries_labels.entries['file_path'].get()
        remark              = self.entries_labels.entries['remark'].get()
        description         = self.entries_labels.entries['description'].get()
        note                = self.entries_labels.entries['note'].get()
        tag                 = self.entries_labels.entries['tag'].get()
        category            = self.entries_labels.entries['category'].get()

        invoice = Invoice(
            id                  = id,
            primary_receiver    = primary_receiver,
            receiver_name       = receiver_name,
            receiver_address    = receiver_address,
            receiver_account    = receiver_account,
            primary_reference   = primary_reference,
            secondary_reference = secondary_reference,
            invoice_date        = invoice_date,
            due_date            = due_date,
            paid_date           = paid_date,
            amount              = amount,
            paying_account_id   = paying_account_id,
            file_path           = file_path,
            remark              = remark,
            description         = description,
            note                = note,
            tag                 = tag,
            category            = category
        )

        if invoice and self.title_str == "Add_Item":
            utils.insert_invoice(self.conn, invoice)
            self.parent.populate_treeview()
        elif invoice and self.title_str == "Edit_Item":
            # update invoice
            utils.update_invoice(self.conn, invoice)
            self.parent.populate_treeview()

        # Update operations view
        self.notebook.children["!operationsview"].populate_treeview()
        self.destroy()


    def validate_fields(self):
        # if not self.primary_receiver_entry.get():
        if not self.entries_labels.entries['primary_receiver'].get():
            tk.messagebox.showerror("Error", "Primary receiver name is required.")
            return False

        try:
            # amount = float(self.amount_entry.get())
            amount = float(self.entries_labels.entries['amount'].get())
        except ValueError:
            tk.messagebox.showerror("Error", "Invalid amount value.")
            return False

        # paying_account = self.paying_account_combo.get()
        paying_account = self.entries_labels.entries['paying_account'].get()
        if not paying_account:
            tk.messagebox.showerror("Error", "Paying account is required.")
            return False

        if not self.get_paying_account_id():
            tk.messagebox.showerror("Error", f"Paying account '{paying_account}' doesn't exist.")
            return False

        # paid_date = self.paid_date_entry.get()
        paid_date = self.entries_labels.entries['paid_date'].get()
        if paid_date and not validation.date_is_valid(paid_date):
            tk.messagebox.showerror("Error", f"paid_date '{paid_date}' is not on format YYYY.MM.DD or YY.M.D or YYYY-MM-DD or YY-M-D.")
            return False

        # due_date = self.due_date_entry.get()
        due_date = self.entries_labels.entries['due_date'].get()
        if due_date and not validation.date_is_valid(due_date):
            tk.messagebox.showerror("Error", f"due_date '{due_date}' is not on format YYYY.MM.DD or YY.M.D or YYYY-MM-DD or YY-M-D.")
            return False

        # invoice_date = self.invoice_date_entry.get()
        invoice_date = self.entries_labels.entries['invoice_date'].get()
        if invoice_date and not validation.date_is_valid(invoice_date):
            tk.messagebox.showerror("Error", f"invoice_date '{invoice_date}' is not on format YYYY.MM.DD or YY.M.D or YYYY-MM-DD or YY-M-D.")
            return False

        return True

    def get_paying_account_id(self):
        # account_description = self.paying_account_combo.get()
        account_description = self.entries_labels.entries['paying_account'].get()
        for account in utils.fetch_accounts(self.conn):
            if account.description == account_description:
                return account.id
        return None

    def populate_fields(self, invoice):
        self.entries_labels.enable_all()

        self.entries_labels.entries['primary_receiver'].insert(0, invoice.primary_receiver)
        self.entries_labels.entries['receiver_name'].insert(0, invoice.receiver_name)
        self.entries_labels.entries['receiver_address'].insert(0, invoice.receiver_address)
        self.entries_labels.entries['receiver_account'].insert(0, invoice.receiver_account)
        self.entries_labels.entries['primary_reference'].insert(0, invoice.primary_reference)
        self.entries_labels.entries['secondary_reference'].insert(0, invoice.secondary_reference)
        self.entries_labels.entries['invoice_date'].insert(0, invoice.invoice_date)
        self.entries_labels.entries['due_date'].insert(0, invoice.due_date)
        self.entries_labels.entries['paid_date'].insert(0, invoice.paid_date)
        self.entries_labels.entries['amount'].insert(0, str(invoice.amount))
        self.entries_labels.entries['paying_account'].set(self.get_account_description(invoice.paying_account_id))
        self.entries_labels.entries['file_path'].insert(0, invoice.file_path)
        self.entries_labels.entries['remark'].insert(0, invoice.remark)
        self.entries_labels.entries['description'].insert(0, invoice.description)
        self.entries_labels.entries['note'].insert(0, invoice.note)
        self.entries_labels.entries['tag'].insert(0, invoice.tag)
        self.entries_labels.entries['category'].insert(0, invoice.category)

        self.entries_labels.reset_all_states()

    def get_account_description(self, account_id):
        for account in utils.fetch_accounts(self.conn):
            if account.id == account_id:
                return account.description
        return None