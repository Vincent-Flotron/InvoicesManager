import tkinter as tk
import Checks.check as check
import utils
from  tkinter                     import font
from  Views.base_view             import BaseView
from  Dialog_elements.entry_label import EntryLabels
from  custom_entries              import *
from  extract                     import *

class AccountsView(BaseView):
    def __init__(self, parent, conn, *args, **kwargs):
        fields_for_columns = ("id", "description", "bank_name", "account_number")
        dialog_class       = AccountDialog
        delete_func        = utils.delete_account
        columns_names      = ['iban' if col_name == 'account_number' else col_name for col_name in fields_for_columns]
        
        super().__init__(parent, conn, "accounts", fields_for_columns, columns_names, dialog_class, delete_func, *args, **kwargs)

    def auto_adjust_column_widths(self):
        for col in self.tree["columns"]:
            max_width = font.Font().measure(col.title())
            for item in self.tree.get_children():
                item_text = self.tree.item(item)["values"][self.tree["columns"].index(col)]
                max_width = max(max_width, font.Font().measure(str(item_text)))
            self.tree.column(col, width=max_width)


class AccountDialog(tk.Toplevel):
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
        self.query_insert      = utils.insert_account
        self.query_update      = utils.update_accounts
        self.query_fetch_by_id = utils.fetch_account_by_id
        self.object_type       = utils.Account

        # Create UI elements to enter account details
        label_frame = tk.LabelFrame(self, text="Account Details")
        label_frame.pack(pady=10, padx=10)
        self.entries_labels = EntryLabels(label_frame, self.many_items)

        self.has_selected_items = True if selected_items else False
        account                 = selected_items[0] if self.has_selected_items else None

        self.entries_labels.make_entry_label("Description",    "description",     Cust_Entry(self.none(account, 'description')),      (check.IsRequired(),),  None,            False)
        self.entries_labels.make_entry_label("Bank Name",      "bank_name",       Cust_Entry(self.none(account, 'bank_name')),        (check.IsRequired(),),  None,            False)
        self.entries_labels.make_entry_label("Account Number", "account_number",  Cust_Entry(self.none(account, 'account_number')),   (check.IsRequired(),),  None,            False)

        # Add buttons to save or cancel
        save_button = tk.Button(self, text="Save", command=self.save)
        save_button.pack()

        cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
        cancel_button.pack()

        # Populate the dialog with account data if editing
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

        # id = self.id
        # description = self.description_entry.get()
        # bank_name = self.bank_name_entry.get()
        # account_number = self.account_number_entry.get()

        # account = Account(
        #     id=id,
        #     description=description,
        #     bank_name=bank_name,
        #     account_number=account_number
        # )

        # self.result = account
        # ttl = self.title_str
        # print("self.title_str " + self.title_str)
        # if self.result and self.title_str == "Add_Item":
        #     utils.insert_account(self.conn, self.result)
        #     self.parent.populate_treeview()
        # elif self.result and self.title_str == "Edit_Item":
        #     utils.update_account(self.conn, self.result)
        #     self.parent.populate_treeview()
        # self.destroy()

        enabled_values        = self.entries_labels.get_enabled_entry_values()
        merged_objects        = None
        if self.has_selected_items:
            # merged_invoices   = self.merge_invoices(    self.selected_items, enabled_values )
            merged_objects    = self.merge_rec_objects(    self.selected_items, enabled_values, self.query_fetch_by_id)
        # invoice_ref           = self.generate_invoices( self.selected_items, enabled_values )[0]
        object_template       = self.generate_rec_objects( self.selected_items, enabled_values, self.object_type)[0]
        self.need_update_view = True

        # Add account
        if object_template  and self.title_str == "Add_Item":
            # utils.insert_invoice(self.conn, object_template)
            self.query_insert(self.conn, object_template)
            self.parent.update_view()

        # Update account
        elif merged_objects and self.title_str == "Edit_Item" and object_template:
            self.query_update(self.conn, merged_objects, object_template)
            self.parent.update_view()

        # Update operations view
        self.notebook.children["!operationsview"].update_view()
        self.destroy()





    def merge_rec_objects(self, selected_items, entry_values, query_rec_object):
        rec_objects = []
        for item in selected_items:
            rec_objects_updated = query_rec_object(self.conn, item.id)
            # Assuming enabled_values is a dictionary with attribute names and functions or keys to get the values
            for name, value in entry_values.items():
                setattr(rec_objects_updated, name, value)
            rec_objects.append(rec_objects_updated)
        return rec_objects
    
    # def generate_an_account(self, selected_items, entry_values):
    #     return self.generate_a_new_rec_obj(selected_items, entry_values, Account)
    

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

    # def populate_fields(self, account):
    #     self.description_entry.insert(0, account.description)
    #     self.bank_name_entry.insert(0, account.bank_name)
    #     self.account_number_entry.insert(0, account.account_number)

    def populate_fields_debug(self):
        self.entries_labels.enable_all()
        self.entries_labels['description'].   insert(0, 'Main account')
        self.entries_labels['bank_name'].     insert(0, 'UBS')
        self.entries_labels['account_number'].insert(0, 'CH45468321356')
        self.entries_labels.reset_all_states()