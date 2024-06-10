import tkinter as tk
from tkinter import ttk
from models import Invoice
import utils
import validation
import format
from Views.base_view import BaseView
from Dialog_elements.entry_label import EntryLabels
import Checks.check as check
from custom_entries import *

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
        self.entries_labels = EntryLabels(label_frame, self.many_items)

        self.entries_labels.make_entry_label("Primary Receiver",   "primary_receiver",    Cust_Entry,     (check.IsRequired(),),                        False)
        self.entries_labels.make_entry_label("Receiver Name",      "receiver_name",       Cust_Entry,     (None),                                       False)
        self.entries_labels.make_entry_label("Receiver Address",   "receiver_address",    Cust_Entry,     (check.IsRequired(),),                        False)
        self.entries_labels.make_entry_label("Receiver Account",   "receiver_account",    Cust_Entry,     (check.IsRequired(),),                        False)
        self.entries_labels.make_entry_label("Primary Reference",  "primary_reference",   Cust_Entry,     (check.IsRequired(),),                        True if self.many_items else False)
        self.entries_labels.make_entry_label("Secondary Reference","secondary_reference", Cust_Entry,     (None),                                       True if self.many_items else False)
        self.entries_labels.make_entry_label("Invoice Date",       "invoice_date",        Cust_Entry,     (check.IsRequired(),   check.IsValidDate()),  False)
        self.entries_labels.make_entry_label("Due Date",           "due_date",            Cust_Entry,     (check.IsRequired(),   check.IsValidDate()),  False)
        self.entries_labels.make_entry_label("Paid Date",          "paid_date",           Cust_Entry,     (check.IsValidDate(),),                       False)
        self.entries_labels.make_entry_label("Amount",             "amount",              Cust_Entry,     (check.IsFloat(),),                           False)
        self.entries_labels.make_entry_label("Paying Account",     "paying_account",      Cust_Combobox,  (check.IsInTable(self.conn, "accounts", "description"),),  False)
        self.entries_labels.make_entry_label("Remark",             "remark",              Cust_Entry,     (None),                                       False)
        self.entries_labels.make_entry_label("Description",        "description",         Cust_Entry,     (None),                                       False)
        self.entries_labels.make_entry_label("Note",               "note",                Cust_Entry,     (None),                                       False)
        self.entries_labels.make_entry_label("Tag",                "tag",                 Cust_Entry,     (None),                                       False)
        self.entries_labels.make_entry_label("Category",           "category",            Cust_Entry,     (None),                                       False)
        self.entries_labels.make_entry_label("File Path",          "file_path",           Cust_file_path, (None),                                       True if self.many_items else False)
        # Populate the paying account combo box
        accounts = utils.fetch_accounts(self.conn)
        self.entries_labels["paying_account"].set_values([account.description for account in accounts])

        # Add buttons to save or cancel
        save_button = tk.Button(self, text="Save", command=self.save)
        save_button.pack()

        cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        cancel_button.pack()

        # Populate the dialog with invoice data if editing
        if item:
            self.populate_fields(item)

    def save(self):
        if not self.validate_fields():
            return

        id                  = self.id
        primary_receiver    = self.entries_labels['primary_receiver'].get_value()
        receiver_name       = self.entries_labels['receiver_name'].get_value()
        receiver_address    = self.entries_labels['receiver_address'].get_value()
        receiver_account    = self.entries_labels['receiver_account'].get_value()
        primary_reference   = self.entries_labels['primary_reference'].get_value()
        secondary_reference = self.entries_labels['secondary_reference'].get_value()
        invoice_date        = self.entries_labels['invoice_date'].get_value()
        invoice_date        =  format.format_date(self.entries_labels['invoice_date'].get_value()) if invoice_date != '' else invoice_date
        due_date            = self.entries_labels['due_date'].get_value()
        due_date            =  format.format_date(self.entries_labels['due_date'].get_value()) if due_date != '' else due_date
        paid_date           = self.entries_labels['paid_date'].get_value()
        paid_date           =  format.format_date(self.entries_labels['paid_date'].get_value()) if paid_date != '' else paid_date
        amount              = round(float(self.entries_labels['amount'].get_value()), 2)
        paying_account_id   = utils.get_paying_account_id_from_descr(self.conn, self.entries_labels['paying_account'].get_value())
        file_path           = self.entries_labels['file_path'].get_value()
        remark              = self.entries_labels['remark'].get_value()
        description         = self.entries_labels['description'].get_value()
        note                = self.entries_labels['note'].get_value()
        tag                 = self.entries_labels['tag'].get_value()
        category            = self.entries_labels['category'].get_value()

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

        # Add invoice
        if invoice and self.title_str == "Add_Item":
            utils.insert_invoice(self.conn, invoice)
            self.parent.populate_treeview()
        # Update invoice
        elif invoice and self.title_str == "Edit_Item":
            utils.update_invoice(self.conn, invoice)
            self.parent.populate_treeview()

        # Update operations view
        self.notebook.children["!operationsview"].populate_treeview()
        self.destroy()
        

    def validate_fields(self):
        self.entries_labels.check_all_entries()
        return True


    def populate_fields(self, invoice):
        self.entries_labels.enable_all()
        self.entries_labels['primary_receiver'].insert(0, invoice.primary_receiver)
        self.entries_labels['receiver_name'].insert(0, invoice.receiver_name)
        self.entries_labels['receiver_address'].insert(0, invoice.receiver_address)
        self.entries_labels['receiver_account'].insert(0, invoice.receiver_account)
        self.entries_labels['primary_reference'].insert(0, invoice.primary_reference)
        self.entries_labels['secondary_reference'].insert(0, invoice.secondary_reference)
        self.entries_labels['invoice_date'].insert(0, invoice.invoice_date)
        self.entries_labels['due_date'].insert(0, invoice.due_date)
        self.entries_labels['paid_date'].insert(0, invoice.paid_date)
        self.entries_labels['amount'].insert(0, str(invoice.amount))
        self.entries_labels['paying_account'].set(utils.get_account_description(self.conn, invoice.paying_account_id))
        self.entries_labels['file_path'].insert(0, invoice.file_path)
        self.entries_labels['remark'].insert(0, invoice.remark)
        self.entries_labels['description'].insert(0, invoice.description)
        self.entries_labels['note'].insert(0, invoice.note)
        self.entries_labels['tag'].insert(0, invoice.tag)
        self.entries_labels['category'].insert(0, invoice.category)
        self.entries_labels.reset_all_states()

