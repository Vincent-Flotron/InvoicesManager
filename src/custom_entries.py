from tkinter import filedialog, Entry, Button, END
from tkinter.ttk import Combobox
from utils import fetch_accounts

class Cust_Entry(Entry):
    def __init__(self, populated_value):
        self.populated_value = populated_value

    def make(self, root, **kwargs):
        super().__init__(root, **kwargs)
        return self

    def populate(self):
        self.insert(0, str(self.populated_value))

class Cust_Combobox(Combobox):
    def __init__(self, choices_list, populated_value):
        self.choices_list     = choices_list
        self.populated_value  = populated_value if populated_value != None else ''

    def make(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self["values"] = self.choices_list
        return self
    
    def populate(self):
        self.set(self.populated_value)

    def prepare_choice_list(self, entry_label):
        self.choices_list
        # Populate the paying account combo box
        accounts = fetch_accounts(self.conn)
        # self.entries_labels[paying_account_id].set_values( [account.description for account in accounts] )
        entry_label.set_values( [account.description for account in accounts] )

class Cust_file_path(Entry):
    def __init__(self, populated_value):
        self.populated_value = populated_value

    def make(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.root = root
        return self
    
    def populate(self):
        self.insert(0, str(self.populated_value))

    def grid(self, row, column, **kwargs):
        super().grid(row=row, column=column, **kwargs)
        # Add a button to open the file browser
        file_button = Button(self.root, text="Select File", command=self.select_file)
        next_col = column + 1
        file_button.grid(row=row, column=next_col)

    def select_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.delete(0, END)
            self.insert(0, file_path)