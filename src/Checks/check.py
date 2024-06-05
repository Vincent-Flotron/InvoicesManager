from tkinter import messagebox
import utils
import validation

class Check:
    def __init__(self):
        self.entry      = ""
        self.entry_name = ""

    def set(self, entry, entry_name):
        self.entry      = entry
        self.entry_name = entry_name

    def check(self):
        raise NotImplementedError("Abstract class")



class IsFloat(Check):
    def __init__(self):
        super().__init__()

    def check(self):
        if self.entry.get():
            try:
                number = float(self.entry.get())
            except ValueError:
                messagebox.showerror("Error", f"{self.entry_name}: value '{str(self.entry.get())}' is not a float")
                return False



class IsInTable(Check):
    def __init__(self, table_name, field_name):
        super().__init__()
        self.table_name  = table_name
        self.field_name  = field_name

    def check(self):
        if self.entry.get():
            res = utils.query(
                f"SELECT {self.field_name} FROM {self.table_name} \
                WHERE {self.field_name} = {self.entry.get()};"
            )
            if len(res) == 0:
                messagebox.showerror("Error", f"{self.entry_name}: value '{self.entry.get()}' is not present in the field '{self.field_name}' of the table '{self.table_name}'.")
                return False
    


class IsRequired(Check):
    def __init__(self):
        super().__init__()

    def check(self):
        if not self.entry.get():
            messagebox.showerror("Error", f"{self.entry_name}: a value is required.")
            return False



class IsValidDate(Check):
    def __init__(self):
        super().__init__()

    def check(self):
        if self.entry.get():
            if not validation.date_is_valid(self.entry.get()):
                messagebox.showerror("Error", f"{self.entry_name}: '{self.entry.get()}' is not on format YYYY.MM.DD or YY.M.D or YYYY-MM-DD or YY-M-D.")
                return False
