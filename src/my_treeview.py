from tkinter import ttk


class MyTreeview(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sort_order = {}
        for field_name in kwargs['columns']:
            self.sort_order[field_name] = False

        # Configure columns for sorting
        for col in self["columns"]:
            self.heading(col, text=col.title(), command=lambda c=col: self.sort_column(c))
            self.heading(col, anchor="center")


    def sort_column(self, col):
        reverse = self.sort_order[col]
        self.sort_order[col] = not reverse

        data = [(self.set(child, col), child) for child in self.get_children("")]
        data.sort(reverse=reverse)

        for index, (value, child) in enumerate(data):
            self.move(child, "", index)

        self.heading(col, command=lambda: self.sort_column(col))