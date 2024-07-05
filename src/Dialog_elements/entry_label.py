import tkinter as tk
from Dialog_elements.enable_entry import EnableEntry


class EntryLabel:
    def __init__(self, label_frame, row_nb, label_text, entry_name, entry_object=tk.Entry, check_objects=None, extract_object=None, locked=False, many_items=False):
        self.label = tk.Label(label_frame, text=f"{label_text}:")
        self.entry = entry_object.make(label_frame)
        self.label.grid(row=row_nb, column=0, sticky="w")
        self.entry.grid(row=row_nb, column=1)
        
        self.ee    = EnableEntry(
            entry              = self.entry,
            label_frame        = label_frame,
            enabled_by_default = not many_items,
            locked             = locked
        )
        self.entry_name     = entry_name
        self.default_state  = self.ee.get_state()
        self.check_objects  = check_objects
        self.init_check_objects()
        self.extract_object = extract_object

    def insert(self, *args, **kwargs):
        self.enable_entry()
        self.entry.insert(*args, **kwargs)
        self.reset_entry()

    def set(self, *args, **kwargs):
        self.enable_entry()
        self.entry.set(*args, **kwargs)
        self.reset_entry()
    
    def get_state(self):
        return self.ee.get_state()
    
    def get_default_state(self):
        return self.default_state
    
    def set_choices(self, values):
        self.entry["values"] = values

    def reset_entry(self):
        if self.get_default_state():
            self.enable_entry()
        else:
            self.disable_entry()

    def enable_entry(self):
        self.ee.enable_entry()

    def disable_entry(self):
        self.ee.disable_entry()

    def init_check_objects(self):
        if self.check_objects:
            for check_object in self.check_objects:
                check_object.set(self.entry, self.entry_name)

    def check(self):
        is_valid = True
        if self.get_state() and self.check_objects:
            for check_object in self.check_objects:
                is_valid = is_valid and check_object.check()
        return is_valid

    def get_name(self):
        return self.entry_name

    def get_value(self):
        if self.extract_object:
            value_extracted = self.extract_object.extract(self.entry.get())
        else:
            value_extracted = self.entry.get()
        return value_extracted
        
    def get_value_if_enabled(self):
        if self.get_state():
            return self.get_value()
        else:
            return None
        


class EntryLabels:
    def __init__(self, label_frame, many_items):
        self.row_nb = 0
        self.entry_labels = {}
        self.label_frame = label_frame
        self.states = []
        self.many_items = many_items

    def make_entry_label(self, label_text, entry_name, entry_type_object=tk.Entry, check_objects=None, extract_object=None, locked=False):
        entry_label = EntryLabel(self.label_frame, self.row_nb, label_text, entry_name, entry_type_object, check_objects, extract_object, locked, self.many_items)
        self.entry_labels[entry_name] = entry_label
        self.row_nb += 1

    def check_all_entries(self):
        all_is_ok = True
        for entry_label in self.entry_labels.values():
            if not entry_label.check():
                all_is_ok = False
        return all_is_ok

    def enable_all(self):
        for entry_label in self.entry_labels.values():
            entry_label.enable_entry()

    def reset_all_states(self):
        for entry_label in self.entry_labels.values():
            entry_label.reset_entry()

    def get_next_row_nb(self):
        return self.row_nb

    def get_enabled_entry_values(self):
        enabled_entry_values = {}
        for _, entry_label in self.entry_labels.items():
            val = entry_label.get_value_if_enabled()
            if val:
                enabled_entry_values[entry_label.get_name()] = val # edit to get enabled value and name given by get_enabled_value. to avoid error with paying_account -> paying_account_id
        return enabled_entry_values

    def __setitem__(self, key, value):
        self.entry_labels[key] = value

    def __getitem__(self, key):
        if key in self.entry_labels:
            return self.entry_labels[key]
        else:
            raise KeyError(f"Key {key} not found")

    def get(self, key, default=None):
        return self.entry_labels.get(key, default)

    def __delitem__(self, key):
        if key in self.entry_labels:
            del self.entry_labels[key]
        else:
            raise KeyError(f"Key {key} not found")

    def __contains__(self, key):
        return key in self.entry_labels

    def __len__(self):
        return len(self.entry_labels)

    def keys(self):
        return self.entry_labels.keys()

    def values(self):
        return self.entry_labels.values()

    def items(self):
        return self.entry_labels.items()
    
    def populate(self):
        for _, entry_label in self.entry_labels.items():
            entry_label.entry.populate()
