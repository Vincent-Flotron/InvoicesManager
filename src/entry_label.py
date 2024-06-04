import tkinter as tk
from enable_entry import EnableEntry

class EntryLabel:
    def __init__(self, label_frame, many_items):
        self.row_nb = 0
        self.labels = {}
        self.entries = {}
        self.enable_list = []
        self.label_frame = label_frame
        self.states = []
        self.many_items = many_items

    def make_entry_label(self, label_text, entry_name, entry_type=tk.Entry):
        self.labels[entry_name] = tk.Label(self.label_frame, text=f"{label_text}:")
        self.labels[entry_name].grid(row=self.row_nb, column=0, sticky="w")
        self.entries[entry_name] = entry_type(self.label_frame)
        self.entries[entry_name].grid(row=self.row_nb, column=1)
        self.row_nb += 1
        # create the EnableEntry instance and set the default state
        self.enable_list.append(
            EnableEntry( self.entries[entry_name],
                         self.label_frame,
                         enabled_by_default=not self.many_items )
        )

    def enable_all(self):
        states = []
        for ee in self.enable_list:
            states.append( ee.get_state() )
            ee.enable_entry()

    def reset_all_states(self):
        for enabled, ee in zip(self.states, self.enable_list):
            if enabled:
                ee.enable_entry()
            else:
                ee.disable_entry()
            
    def get_next_row_nb(self):
        return self.row_nb