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
        return self

    def check(self):
        raise NotImplementedError("Abstract class")


class IsFloat(Check):
    def __init__(self):
        super().__init__()

    def check(self):
        return_value = False
        if self.entry.get():
            try:
                number = float(self.entry.get())
                return_value = True
            except ValueError:
                return_value = False # messagebox.showerror("Error", f"{self.entry_name}: value '{str(self.entry.get())}' is not a float")
        if not return_value:
            messagebox.showerror("Error", f"{self.entry_name}: value '{str(self.entry.get())}' is not a float") 
        return return_value


class IsInTable(Check):
    def __init__(self, conn, table_name, field_name):
        super().__init__()
        self.table_name  = table_name
        self.field_name  = field_name
        self.conn        = conn

    def check(self):
        return_value = True
        if self.entry.get():
            res = utils.query(
                self.conn,
                f"SELECT {self.field_name} FROM {self.table_name} \
                WHERE {self.field_name} = '{self.entry.get()}';"
            )
            if len(res) == 0:
                messagebox.showerror("Error", f"{self.entry_name}: value '{self.entry.get()}' is not present in the field '{self.field_name}' of the table '{self.table_name}'.")
                return_value = False
        return return_value
    


class IsRequired(Check):
    def __init__(self):
        super().__init__()

    def check(self):
        return_value = True
        if not self.entry.get():
            messagebox.showerror("Error", f"{self.entry_name}: a value is required.")
            return_value = False
        return return_value



class IsValidDate(Check):
    def __init__(self):
        super().__init__()

    def check(self):
        return_value = True
        if self.entry.get():
            if not validation.date_is_valid(self.entry.get()):
                messagebox.showerror("Error", f"{self.entry_name}: '{self.entry.get()}' is not on format YYYY.MM.DD or YY.M.D or YYYY-MM-DD or YY-M-D.")
                return_value = False
        return return_value
