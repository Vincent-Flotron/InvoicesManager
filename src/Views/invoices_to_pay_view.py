import tkinter      as tk
import Checks.check as check
import utils
from  tkinter                     import font
from  Views.base_view             import BaseView
from  Dialog_elements.entry_label import EntryLabels
from  custom_entries              import *
from  extract                     import *


class InvoicesToPayView(BaseView):
    def __init__(self, parent, conn, *args, **kwargs):
        fields_for_columns = ("id", "primary_receiver", "receiver_name", "receiver_address", "receiver_account", "primary_reference", "secondary_reference", "invoice_date", "due_date", "paid_date", "amount", "file_path")
        dialog_class = InvoiceDialog
        delete_func = utils.delete_invoice
        columns_names = fields_for_columns
        super().__init__(parent, conn, "invoices_to_pay", fields_for_columns, columns_names, dialog_class, delete_func, *args, **kwargs)
        self.auto_adjust_column_widths()

    def auto_adjust_column_widths(self):
        for col in self.tree["columns"]:
            max_width = font.Font().measure(col.title())
            for item in self.tree.get_children():
                item_text = self.tree.item(item)["values"][self.tree["columns"].index(col)]
                max_width = max(max_width, font.Font().measure(str(item_text)))
            self.tree.column(col, width=max_width)


class InvoiceDialog(tk.Toplevel):
    def DEBUG(self):
        if self.title_str == "Add_Item":
            self.populate_fields_debug()

    def __init__(self, parent, notebook, title, selected_items=None):
        super().__init__(parent)
        self.title(title)
        self.title_str        = title
        self.conn             = parent.conn
        self.parent           = parent
        self.notebook         = notebook
        self.selected_items   = selected_items
        if selected_items:
            self.many_items   = len(selected_items) > 1
            self.id           = selected_items[0].id
        else:
            self.many_items   = False
            self.id           = None
        self.need_update_view = False

        # Queries
        self.query_insert      = utils.insert_invoice
        self.query_update      = utils.update_invoices
        self.query_fetch_by_id = utils.fetch_invoice_by_id
        self.object_type       = utils.Invoice

        # Create UI elements to enter invoice details
        label_frame         = tk.LabelFrame(self, text="Invoice Details")
        label_frame.pack(pady=10, padx=10)
        self.entries_labels = EntryLabels(label_frame, self.many_items)

        # Get first invoice of the selection
        self.has_selected_items = True if selected_items else False
        first_invoice           = selected_items[0] if self.has_selected_items else None
        # Get actual paying account linked to the first invoice
        act_paying_account_id   = selected_items[0].paying_account_id if self.has_selected_items else ""
        act_paying_account      = utils.get_account_description(self.conn, act_paying_account_id)

        # Set input fields
        paying_account_cb = Cust_Combobox([account.description for account in utils.fetch_accounts(self.conn)], act_paying_account)
        self.entries_labels.make_entry_label("Primary Receiver",   "primary_receiver",    Cust_Entry(self.none(first_invoice, 'primary_receiver')),    (check.IsRequired(),),                        None,            False)
        self.entries_labels.make_entry_label("Receiver Name",      "receiver_name",       Cust_Entry(self.none(first_invoice, 'receiver_name')),       (None),                                       None,            False)
        self.entries_labels.make_entry_label("Receiver Address",   "receiver_address",    Cust_Entry(self.none(first_invoice, 'receiver_address')),    (check.IsRequired(),),                        None,            False)
        self.entries_labels.make_entry_label("Receiver Account",   "receiver_account",    Cust_Entry(self.none(first_invoice, 'receiver_account')),    (check.IsRequired(),),                        None,            False)
        self.entries_labels.make_entry_label("Primary Reference",  "primary_reference",   Cust_Entry(self.none(first_invoice, 'primary_reference')),   (check.IsRequired(),),                        None,            True if self.many_items else False)
        self.entries_labels.make_entry_label("Secondary Reference","secondary_reference", Cust_Entry(self.none(first_invoice, 'secondary_reference')), (None),                                       None,            True if self.many_items else False)
        self.entries_labels.make_entry_label("Invoice Date",       "invoice_date",        Cust_Entry(self.none(first_invoice, 'invoice_date')),        (check.IsRequired(),   check.IsValidDate()),  ExtractDate(),   False)
        self.entries_labels.make_entry_label("Due Date",           "due_date",            Cust_Entry(self.none(first_invoice, 'due_date')),            (check.IsRequired(),   check.IsValidDate()),  ExtractDate(),   False)
        self.entries_labels.make_entry_label("Paid Date",          "paid_date",           Cust_Entry(self.none(first_invoice, 'paid_date')),           (check.IsValidDate(),),                       ExtractDate(),   False)
        self.entries_labels.make_entry_label("Amount",             "amount",              Cust_Entry(self.none(first_invoice, 'amount')),              (check.IsFloat(),),                           ExtractAmount(), False)
        self.entries_labels.make_entry_label("Paying Account",     "paying_account_id",   paying_account_cb,                                           (check.IsInTable(self.conn, "accounts", "description"),),
                                                                                                                                                                                                     ExtractUsingQuery(self.conn, utils.get_paying_account_id_from_descr),
                                                                                                                                                                                                                      False)
        self.entries_labels.make_entry_label("Remark",             "remark",              Cust_Entry(self.none(first_invoice,  'remark')),             (None),                                       None,            False)
        self.entries_labels.make_entry_label("Description",        "description",         Cust_Entry(self.none(first_invoice,  'description')),        (None),                                       None,            False)
        self.entries_labels.make_entry_label("Note",               "note",                Cust_Entry(self.none(first_invoice,  'note')),               (None),                                       None,            False)
        self.entries_labels.make_entry_label("Tag",                "tag",                 Cust_Entry(self.none(first_invoice,  'tag')),                (None),                                       None,            False)
        self.entries_labels.make_entry_label("Category",           "category",            Cust_Entry(self.none(first_invoice,  'category')),           (None),                                       None,            False)
        self.entries_labels.make_entry_label("File Path",          "file_path",           Cust_file_path(self.none(first_invoice,'file_path')),        (None),                                       None,            True if self.many_items else False)

        # Buttons to save or cancel
        save_button   = tk.Button(self, text="Save", command=self.save)
        save_button.pack()
        cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        cancel_button.pack()

        # Populate the dialog with invoice data if editing
        if self.has_selected_items:
            self.entries_labels.populate()
        
        self.DEBUG()

    def none(self, object, field):
        if object:
            return getattr(object, field)
        else:
            return None
        
    def save(self):
        if not self.validate_fields():
            return

        enabled_values        = self.entries_labels.get_enabled_entry_values()
        merged_objects        = None
        if self.has_selected_items:
            # merged_invoices   = self.merge_invoices(    self.selected_items, enabled_values )
            merged_objects    = self.merge_rec_objects(    self.selected_items, enabled_values, self.query_fetch_by_id)
        # invoice_ref           = self.generate_invoices( self.selected_items, enabled_values )[0]
        object_template       = self.generate_rec_objects( self.selected_items, enabled_values, self.object_type)[0]
        self.need_update_view = True

        # Add invoice
        if object_template  and self.title_str == "Add_Item":
            # utils.insert_invoice(self.conn, object_template)
            self.query_insert(self.conn, object_template)
            self.parent.update_view()

        # Update invoice
        elif merged_objects and self.title_str == "Edit_Item" and object_template:
            self.query_update(self.conn, merged_objects, object_template)
            self.parent.update_view()

        # Update operations view
        self.notebook.children["!operationsview"].update_view()
        self.destroy()

    # def merge_invoices(self, selected_items, entry_values):
    #     return self.merge_rec_objects(selected_items, entry_values, utils.fetch_invoice_by_id)

    def merge_rec_objects(self, selected_items, entry_values, query_rec_object):
        rec_objects = []
        for item in selected_items:
            rec_objects_updated = query_rec_object(self.conn, item.id)
            # Assuming enabled_values is a dictionary with attribute names and functions or keys to get the values
            for name, value in entry_values.items():
                setattr(rec_objects_updated, name, value)
            rec_objects.append(rec_objects_updated)
        return rec_objects
    
    # def generate_invoices(self, selected_items, entry_values):
    #     return self.generate_rec_objects(selected_items, entry_values, Invoice)
    
    def generate_rec_objects(self, selected_items, entry_values, rec_obj_type):
        rec_objects = []
        if selected_items:
            for item in selected_items:
                invoice = self.generate_a_rec_obj(item, entry_values, rec_obj_type)

                rec_objects.append(invoice)
        else:
            invoice = self.generate_a_rec_obj(None, entry_values, rec_obj_type)
            invoice_cleaned = self.replace_none_fields(invoice)
            rec_objects.append(invoice_cleaned)
        return rec_objects

    def replace_none_fields(self, object_with_none_fields):
        # print all properties and their values
        for prop_name, prop_value in object_with_none_fields.__dict__.items():
            if prop_name != 'id' and prop_value == None:
                setattr(object_with_none_fields, prop_name, '')
        object_without_none_fields = object_with_none_fields
        return object_without_none_fields
    
    def generate_a_rec_obj(self, selected_items, entry_values, rec_obj_type):
        rec_obj = rec_obj_type()
        # Assuming enabled_values is a dictionary with attribute names and functions or keys to get the values
        for name, value in entry_values.items():
            setattr(rec_obj, name, value)
        if selected_items:
            rec_obj.id = selected_items.id
        return rec_obj

    def validate_fields(self):
        all_is_ok = self.entries_labels.check_all_entries()
        return all_is_ok


    def populate_fields_debug(self):
        self.entries_labels.enable_all()
        self.entries_labels['primary_receiver'].   insert(0, 'Vincent')
        self.entries_labels['receiver_name'].      insert(0, 'Po')
        self.entries_labels['receiver_address'].   insert(0, 'Impasse bleue')
        self.entries_labels['receiver_account'].   insert(0, 'CH76458756327823')
        self.entries_labels['primary_reference'].  insert(0, '765465436543564')
        self.entries_labels['secondary_reference'].insert(0, '')
        self.entries_labels['invoice_date'].       insert(0, '20.02.2024')
        self.entries_labels['due_date'].           insert(0, '22.03.2024')
        self.entries_labels['paid_date'].          insert(0, '')
        self.entries_labels['amount'].             insert(0, '1204')
        self.entries_labels['paying_account_id'].  set('')
        self.entries_labels['file_path'].          insert(0, '')
        self.entries_labels['remark'].             insert(0, '')
        self.entries_labels['description'].        insert(0, '')
        self.entries_labels['note'].               insert(0, '')
        self.entries_labels['tag'].                insert(0, '')
        self.entries_labels['category'].           insert(0, '')
        self.entries_labels.reset_all_states()

