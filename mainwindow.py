import tkinter as tk
from tkinter import *
import customtkinter as ctk
from search import get_layout, insert_newlines, search_name, truncate_text
from tkinter import font

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.database_root = "C:/Users/choff/OneDrive/Bureau/TB/BIDS_Database"  # path to the root directory of all your datasets
        self.title("BIDS Search App")
        self.name_font = font.Font(family='Helvetica', size=10, weight='bold')
        self.path_font = font.Font(family='Helvetica', size=10)
        
    
        # TOP FRAME
        # Top frame for filters
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", pady=(20, 10), padx=20)
        
        # Title for Database Filters
        self.filter_label = Label(self.top_frame, text="Database Filters :", anchor="w")
        self.filter_label.pack(pady=10, padx=5, anchor="w")

        # Label and Entry for search keyword
        self.name_label = Label(self.top_frame, text="Dataset Name: ")
        self.name_label.pack(side="left", pady=10, padx=5)
        
        self.keyword_entry = Entry(self.top_frame)
        self.keyword_entry.pack(side="left", fill="none", expand=False)
        
        
        
        
        # SEARCH BUTTON
        # Button to initiate search
        self.search_btn = ctk.CTkButton(self, text="Search", command=self.search_datasets)
        self.search_btn.pack(padx=20, fill="x")




        # BOTTOM RESULTS
        # Bottom scrollable frame for results
        self.bottom_frame = ctk.CTkScrollableFrame(self, height=500) 
        self.bottom_frame.pack(fill="x", pady=(10), padx=20, expand=True)

        # Title for Results
        self.result_title_label = Label(self.bottom_frame, text="Results :", anchor="w")
        self.result_title_label.pack(pady=10, padx=5, anchor="w")

        # Label to display search results
        self.result_label = Label(self.bottom_frame, text="", anchor="w", justify="left")
        self.result_label.pack(pady=20, padx=5, anchor="w", fill="x")
        self.result_label.config(text="Welcome, please enter a filter and press Search.")


    def search_datasets(self):
        keyword = self.keyword_entry.get()
        matching_datasets = search_name(self.database_root, keyword)

        # Clear previous results
        for widget in self.bottom_frame.winfo_children():
            widget.destroy()

        if matching_datasets:
            for name, path, readme_preview in matching_datasets:
                # Create a Label for the dataset name
                name_label = Label(self.bottom_frame, text=truncate_text(name, 100), anchor="w", justify="left", foreground="black", font=self.name_font)
                name_label.pack(pady=(5, 0), padx=5, anchor="w", fill="x")

                # Create a Label for the dataset path
                path_label = Label(self.bottom_frame, text=path, anchor="w", justify="left", foreground="green", font=self.path_font)
                path_label.pack(pady=(0, 0), padx=5, anchor="w", fill="x")

                # Create a Label for the README preview
                readme_label = Label(self.bottom_frame, text=truncate_text(insert_newlines(readme_preview, 125),500), anchor="w", justify="left", font=self.path_font)
                readme_label.pack(pady=(0, 10), padx=5, anchor="w", fill="x")
        else:
            no_result_label = Label(self.bottom_frame, text="No matching datasets found.", anchor="w", justify="left")
            no_result_label.pack(pady=20, padx=5, anchor="w", fill="x")
            
    
    
