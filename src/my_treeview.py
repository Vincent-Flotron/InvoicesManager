from tkinter import ttk


class MyTreeview(ttk.Treeview):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.detached_row = None
        self.sort_order = {}
        for field_name in kwargs['columns']:
            self.sort_order[field_name] = False

        # Configure columns for sorting
        for col in self["columns"]:
            self.heading(col, text=col.title(), command=lambda c=col: self.sort_column(c))
            self.heading(col, anchor="center")

    # def sort_column(self, col):
    #     reverse = self.sort_order[col]
    #     self.sort_order[col] = not reverse
    #     eadings = self.heading
    #     children = []
    #     for child in self.get_children(""):
    #         children.append(child)

            
    #     data = [(self.set(child, col), child, child if "actual sold" in self.set(child, col) else None) for child in self.get_children("")]
    #     data.sort(key=lambda x: (x[2] is not None, x[0],), reverse=reverse)

    #     for index, (value, child, _) in enumerate(data):
    #         self.move(child, "", index)
    #         self.heading(col, command=lambda: self.sort_column(col))

    # def sort_column(self, col, reverse):
    #     data_list = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
    #     if col in ['income', 'outcome']:
    #         data_list = [(float(value), child) for value, child in data_list if value]
    #     data_list.sort(reverse=reverse)
    #     for index, (val, child) in enumerate(data_list):
    #         self.tree.move(child, '', index)
    #     self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))

    def sort_column(self, col):
        actual_sold_row_id = self.remove_actual_sold()
        reverse = self.sort_order[col]
        self.sort_order[col] = not reverse

        data = [(self.set(child, col), child) for child in self.get_children("")]
        if col in ['income', 'outcome']:
            data = [(float(value), child) for value, child in data if value]
        data.sort(reverse=reverse)

        for index, (value, child) in enumerate(data):
            self.move(child, "", index)

        self.heading(col, command=lambda: self.sort_column(col))
        self.re_insert_actual_sold(actual_sold_row_id)

    def remove_actual_sold(self):
        type_value = None
        # Get the column names
        column_names = self.cget('columns')

        # iterate over the rows of the treeview
        for row_id in self.get_children(""):
            # get the value of the "type" cell in the current row
            if 'type' in column_names:
                type_value = self.set(row_id, "type")


            # if the value of the "type" cell is "actual_sold", delete the row
            if type_value == "actual sold":
                self.detach(row_id)
                return row_id
                # break  # exit the loop after deleting the first matching row
        # return detached_row
        return None
    
    def re_insert_actual_sold(self, actual_sold_row_id):
        # reinsert the detached row at the end of the treeview
        if actual_sold_row_id != None:
            self.insert("", "end", values=self.item(actual_sold_row_id)['values'])

    def edit_a_row(self, row_to_edit="i002", value=""):
        # get the list of columns in the treeview
        columns = self.get_children("")[0].split(" ")[1:]

        # iterate over the columns and modify the value of each cell in the row
        for col in columns:
            # get the current value of the cell
            value = self.set(row_to_edit, col)

            # modify the value (e.g., convert it to uppercase)
            new_value = value

            # set the new value of the cell
            self.set(row_to_edit, col, new_value)