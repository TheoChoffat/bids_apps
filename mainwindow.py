import tkinter as tk
from tkinter import filedialog, Entry, Label
from search import get_layout, search_in_description

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.database_root = "C:/Users/choff/OneDrive/Bureau/TB/BIDS_Database"  # path to the root directory of all your datasets

        self.title("BIDS Search App")
        
        # Entry for search keyword
        self.keyword_entry = Entry(self)
        self.keyword_entry.pack(pady=20)
        
        # Button to initiate search
        self.search_btn = tk.Button(self, text="Search", command=self.search_datasets)
        self.search_btn.pack(pady=20)

        # Label to display search results
        self.result_label = Label(self, text="")
        self.result_label.pack(pady=20)

    def search_datasets(self):
        keyword = self.keyword_entry.get()
        matching_datasets = search_in_description(self.database_root, keyword)

        # Display the results in the result_label
        if matching_datasets:
            self.result_label.config(text="\n Dataset Name : ".join(matching_datasets))
        else:
            self.result_label.config(text="No matching datasets found.")