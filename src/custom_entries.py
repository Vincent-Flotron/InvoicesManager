from tkinter import filedialog, Entry, Button, END
from tkinter.ttk import Combobox

class Cust_Entry(Entry):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)

class Cust_Combobox(Combobox):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)

class Cust_file_path(Entry):
    def __init__(self, root, **kwargs):
        super().__init__(root, **kwargs)
        self.root = root

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