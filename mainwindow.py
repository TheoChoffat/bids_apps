import tkinter as tk
from tkinter import *
import customtkinter as ctk
from search import get_layout, insert_newlines, search_name, search_participant, truncate_text
from tkinter import font
from tkinter import filedialog
from .ctk_rangeslider import CTkRangeSlider

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
        
        
        # SETTINGS FRAME
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(fill="x", pady=(10,0), padx=20)
        
        self.database_path_button = ctk.CTkButton(self.settings_frame, text="Database Path", command=self.change_database_path)
        self.database_path_button.pack(side="left", padx=(0,10))

        self.database_path_display = Label(self.settings_frame, text=self.database_root, anchor="w")
        self.database_path_display.pack(side="left", fill="x", expand=True, padx=(0,10))
    
    
        # TOP FRAME
        # Top frame for filters
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", pady=(10, 10), padx=20)
        
        # DATABASE FILTERS
        # Name dataset filter
        self.filter_label = Label(self.top_frame, text="Database Filters :", anchor="w")
        self.filter_label.pack(pady=(10,0), padx=5, anchor="w")
        self.name_label = Label(self.top_frame, text="Dataset Name: ")
        self.name_label.pack(side="left", pady=10, padx=5)
        self.keyword_entry = Entry(self.top_frame)
        self.keyword_entry.pack(side="left", fill="none", expand=False)
        
        # Participant.tsv age filter
        self.age_label = Label(self.top_frame, text="Age Range: ")
        self.age_label.pack(side="left", pady=10, padx=5)
        self.age_min_label = Label(self.top_frame, text="0")
        self.age_min_label.pack(side="left", pady=10, padx=5)
        self.age_range = (0, 100)
        self.age_slider = CTkRangeSlider(self.top_frame, from_=0, to=100)
        self.age_slider.pack(side="left", padx=10)
        self.age_slider.set(self.age_range)
        self.age_slider.bind("<ButtonRelease-1>", self.update_age_labels)
        self.age_max_label = Label(self.top_frame, text="100")
        self.age_max_label.pack(side="left", pady=10, padx=5)
        
        
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
        keyword = self.keyword_entry.get().strip()
        age_range = self.age_slider.get()

        if not isinstance(age_range, tuple) or len(age_range) != 2:
            age_range = (0, 100)

        datasets_by_name = {}
        datasets_by_participant = {}

        if keyword:
            datasets_by_name = {tuple(dataset[:3]): dataset for dataset in search_name(self.database_root, keyword)}
        else:
            datasets_by_name = {tuple(dataset[:3]): dataset for dataset in search_participant(self.database_root, age_range=age_range)}

        if age_range != (0, 100):
            datasets_by_participant = {tuple(dataset[:3]): dataset for dataset in search_participant(self.database_root, age_range=age_range)}
        else:
            datasets_by_participant = datasets_by_name

        # Determine the final set of matching datasets.
        matching_datasets = {key: value for key, value in datasets_by_name.items() if key in datasets_by_participant}

        # Convert back to list
        matching_datasets = list(matching_datasets.values())

        # Clear previous results
        for widget in self.bottom_frame.winfo_children():
            widget.destroy()

        if matching_datasets:
            for dataset in matching_datasets:
                if len(dataset) == 3:  # This is from search_name function
                    name, path, readme_preview = dataset
                    
                    # rest of your code for displaying these datasets
                    name_label = Label(self.bottom_frame, text=truncate_text(name, 100), anchor="w", justify="left", foreground="black", font=self.name_font)
                    name_label.pack(pady=(5, 0), padx=5, anchor="w", fill="x")
                    
                    path_label = Label(self.bottom_frame, text=path, anchor="w", justify="left", foreground="green", font=self.path_font)
                    path_label.pack(pady=(0, 0), padx=5, anchor="w", fill="x")

                    readme_label = Label(self.bottom_frame, text=truncate_text(insert_newlines(readme_preview, 125), 500), anchor="w", justify="left", font=self.path_font)
                    readme_label.pack(pady=(0, 10), padx=5, anchor="w", fill="x")

                elif len(dataset) == 4:  # This is from search_participant function
                    name, path, readme_preview, matched_participants = dataset
                    
                    # Code for displaying the dataset details similar to above
                    name_label = Label(self.bottom_frame, text=truncate_text(name, 100), anchor="w", justify="left", foreground="black", font=self.name_font)
                    name_label.pack(pady=(5, 0), padx=5, anchor="w", fill="x")
                    
                    path_label = Label(self.bottom_frame, text=path, anchor="w", justify="left", foreground="green", font=self.path_font)
                    path_label.pack(pady=(0, 0), padx=5, anchor="w", fill="x")

                    readme_label = Label(self.bottom_frame, text=truncate_text(insert_newlines(readme_preview, 125), 500), anchor="w", justify="left", font=self.path_font)
                    readme_label.pack(pady=(0, 10), padx=5, anchor="w", fill="x")
                    
                    # Display matched participants
                    for participant_id, age in matched_participants:
                        if age is not None:
                            participant_label = Label(self.bottom_frame, text=f"Participant: {participant_id}, Age: {age}", anchor="w", justify="left", font=self.path_font)
                        else:
                            participant_label = Label(self.bottom_frame, text=f"Participant: {participant_id}", anchor="w", justify="left", font=self.path_font)
                        participant_label.pack(pady=(0, 5), padx=5, anchor="w", fill="x")
        else:
            no_result_label = Label(self.bottom_frame, text="No matching datasets found.", anchor="w", justify="left")
            no_result_label.pack(pady=20, padx=5, anchor="w", fill="x")
            
    
    def update_age_range(self, event=None):
        """ Update the age range based on the slider values. """
        self.age_range = self.age_slider.get()
        
    def update_age_labels(self, event=None):
        """ Update the age labels with the current slider values. """
        min_value, max_value = self.age_slider.get()
        self.age_min_label.config(text=str(int(min_value)))
        self.age_max_label.config(text=str(int(max_value)))

    def change_database_path(self):
        """ Open a file dialog to choose a new database root path """
        new_path = filedialog.askdirectory(title="Select the Database Root Directory")
        if new_path:  # Only update if a new path is selected
            self.database_root = new_path
            self.database_path_display.config(text=self.database_root)