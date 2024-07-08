import tkinter as tk

class LockEntry:
    def __init__(self, entry, label_frame, enabled_by_default=True, locked=False):
        self.entry = entry
        self.label_frame = label_frame
        self.var = tk.BooleanVar()
        self.var.set(enabled_by_default)
        self.locked = locked
        if locked:
            self.var.set(False)

        # grid the check button in the same row and column as the entry
        row = self.entry.grid_info()["row"]
        # next_column = self.entry.grid_info()["column"] + 1
        next_column = 4
        self.check_button = tk.Checkbutton(self.label_frame, variable=self.var, command=self.toggle_entry)
        self.check_button.grid(row=row, column=next_column)

        # set the initial state of the entry
        self.toggle_entry()

    def get_state(self):
        return self.var.get()

    def toggle_entry(self):
        if self.var.get() and not self.locked:
            self.enable_entry()
        else:
            self.disable_entry()

    def enable_entry(self):
        if not self.locked:
            self.entry.config(state="normal")
    
    def disable_entry(self):
        self.entry.config(state="disabled")