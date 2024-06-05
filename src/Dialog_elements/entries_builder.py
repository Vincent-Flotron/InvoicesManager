from Dialog_elements.entry_label import EntryLabel

class EntriesBuilder():
    def __init__(self, label_frame, many_items):
        self.label_frame = label_frame
        self.entries_labels = EntryLabel(self.label_frame, many_items)

    def make_entries(self, label_texts, entry_names, entry_types, checks_list, allowed_when_multi_edition):
        entries_labels = []
        for label_text, entry_name, entry_type, checks, allo_when_mult_edit in zip(label_texts, entry_names, entry_types, checks_list, allowed_when_multi_edition):
            entries_labels.make_entry_label(label_text, entry_name, entry_type, checks, allo_when_mult_edit)