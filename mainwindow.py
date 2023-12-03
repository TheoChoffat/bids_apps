import tkinter as tk
import os
from tkinter import *
from tkinter import ttk
import customtkinter as ctk
from search import get_layout, insert_newlines, search_name, search_participant, truncate_text
from tkinter import font
from tkinter import filedialog
from .ctk_rangeslider import CTkRangeSlider

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class MainWindow(tk.Tk):
    def __init__(self):
        '''
        Initialize the main window of the application.
        
        Sets up the geometry, title, icon, fonts, and the settings frame of the main window.
        '''
        super().__init__()
        self.geometry("800x600")
        self.database_root = "C:/Enter/The/BIDS/Database/BIDS_Database"  # path to the root directory of all your datasets
        self.title("BIDS Search App")
        self.iconbitmap(r'logo_BIDS_apps.ico')
        
        # Set the fonts for use in the application
        self.name_font = font.Font(family='Helvetica', size=10, weight='bold')
        self.path_font = font.Font(family='Helvetica', size=10)
        
        # Initialize the settings frame
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(fill="x", pady=(10,0), padx=20)
        
        # Initialize database path settings
        self.database_path_button = ctk.CTkButton(self.settings_frame, text="Database Path", command=self.change_database_path)
        self.database_path_button.pack(side="left", padx=(0,10))

        # Display for showing the current database path
        self.database_path_display = Label(self.settings_frame, text=self.database_root, anchor="w")
        self.database_path_display.pack(side="left", fill="x", expand=True, padx=(0,10))
    
        # Top frame for filters
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(fill="x", pady=(10, 10), padx=20)

        # Database Filters Section
        # Label for database filters
        self.filter_label = Label(self.top_frame, text="Database Filters :", anchor="w", background="#DBDBDB", font=self.name_font)
        self.filter_label.grid(row=0, column=0, columnspan=3, pady=(10, 0), padx=5, sticky="w")

        # Label for dataset name filter
        self.name_label = Label(self.top_frame, text="Dataset Name: ", background="#DBDBDB")
        self.name_label.grid(row=1, column=0, pady=10, padx=5, sticky="w")
        
        # Input field for dataset name keyword
        self.keyword_entry = Entry(self.top_frame)
        self.keyword_entry.grid(row=1, column=1, columnspan=2, pady=10, padx=5, sticky="ew")

        # Participant.tsv age filter
        self.age_label = Label(self.top_frame, text="Age Range: ", background="#DBDBDB")
        self.age_label.grid(row=2, column=0, pady=10, padx=5, sticky="w")
        
        # Minimum age label for the age filter
        self.age_min_label = Label(self.top_frame, text="0", background="#DBDBDB", foreground="#3B8ED0", font=self.name_font)
        self.age_min_label.grid(row=2, column=1, pady=10, padx=0, sticky="w")
        
        # Age range slider for selecting age range
        self.age_range = (0, 100)
        self.age_slider = CTkRangeSlider(self.top_frame, from_=0, to=100)
        self.age_slider.grid(row=2, column=2, pady=10, padx=0, sticky="ew")
        self.age_slider.set(self.age_range)
        self.age_slider.bind("<ButtonRelease-1>", self.update_age_labels)
        
        # Maximum age label for the age filter
        self.age_max_label = Label(self.top_frame, text="100", background="#DBDBDB", foreground="#3B8ED0", font=self.name_font)
        self.age_max_label.grid(row=2, column=3, pady=10, padx=(0,10), sticky="w")
        
        # Participant.tsv sex filter label
        self.sex_label = Label(self.top_frame, text="Gender: ", background="#DBDBDB")
        self.sex_label.grid(row=2, column=4, pady=10, padx=10, sticky="ew")

        # Participant.tsv sex filter parameters
        self.sex_options = ["", "Male (M)", "Female (F)", "Others (O)"]
        self.sex_combobox = ttk.Combobox(self.top_frame, values=self.sex_options, width=12)
        self.sex_combobox.grid(row=2, column=5, pady=10, padx=10, sticky="ew")
        
        # Button to initiate search
        self.search_btn = ctk.CTkButton(self, text="Search", command=self.search_datasets)
        self.search_btn.pack(padx=20, fill="x")

        # Bottom scrollable frame for results
        self.bottom_frame = ctk.CTkScrollableFrame(self, height=500) 
        self.bottom_frame.pack(fill="x", pady=(10), padx=20, expand=True)

        # Title for Results
        self.result_title_label = Label(self.bottom_frame, text="Results :", anchor="w", background="#DBDBDB", font=self.name_font)
        self.result_title_label.pack(pady=10, padx=5, anchor="w")

        # Label to display search results
        self.result_label = Label(self.bottom_frame, text="", anchor="w", justify="left", background="#DBDBDB")
        self.result_label.pack(pady=20, padx=5, anchor="w", fill="x")
        self.result_label.config(text="Welcome, please enter a filter and press Search.")


    def search_datasets(self):
        '''
        Search for datasets based on user-entered keyword, age range, and sex.
        Updates the results frame with matching datasets.

        - Retrieves the keyword from the keyword entry field.
        - Gets the selected age range from the age slider.
        - Obtains the selected sex from the sex variable.
        - Destroys the previous results frame and creates a new one for displaying search results.
        - Performs a search by name keyword using the search_name function.
        - If additional filters (age range or sex) are provided, it further filters the datasets
        using the search_participant function.
        - For each matching dataset, creates a button in the results frame to allow further interaction.
        '''
        keyword = self.keyword_entry.get().strip()
        age_range = self.age_slider.get()
        selected_sex = self.sex_combobox.get()

        # Transform the gender selection to match the real filtering
        if selected_sex == "Male (M)":
            filter_sex = "M"
        elif selected_sex == "Female (F)":
            filter_sex = "F"
        elif selected_sex == "Others (O)":
            filter_sex = "O"
        else:
            filter_sex = "all"

        # Validate and set the default age range if not properly specified
        if not isinstance(age_range, tuple) or len(age_range) != 2:
            age_range = (0, 100)  # Default age range covering all ages

        # Check if no filter is active (i.e., no keyword, default age range, and 'all' sexes selected)
        no_filter_active = not keyword and age_range == (0, 100) and filter_sex == "all"

        # Initialize dictionaries to hold datasets filtered by name and participant criteria
        datasets_by_name = {}
        datasets_by_participant = {}

        # If a keyword is provided, search datasets by name and store them in a dictionary
        # The key is a tuple of the first three elements (assumed to be identifiers) of each dataset
        if keyword:
            datasets_by_name = {tuple(dataset[:3]): dataset for dataset in search_name(self.database_root, keyword)}

        # Search datasets by participant criteria and store them in a dictionary
        # Uses age range and sex filters; applies no filter if none are active
        datasets_by_participant = {tuple(dataset[:3]): dataset for dataset in search_participant(self.database_root, age_range=age_range, sex=filter_sex, no_filter=no_filter_active)}

        # Determine the final set of matching datasets based on the applied filters
        # If a keyword is used, find the intersection of datasets_by_name and datasets_by_participant
        # If no keyword is used, all datasets matching the participant criteria are selected
        if keyword:
            if datasets_by_participant:
                matching_datasets = {k: v for k, v in datasets_by_name.items() if k in datasets_by_participant}
            else:
                matching_datasets = datasets_by_name
        else:
            matching_datasets = datasets_by_participant

        # Convert the final matching datasets from a dictionary back to a list
        matching_datasets = list(matching_datasets.values())

        # Clear previous results from the bottom frame before displaying new results
        for widget in self.bottom_frame.winfo_children():
            widget.destroy()

        # Check if any datasets match the search criteria
        if matching_datasets:
            # Iterate over each matching dataset
            for dataset in matching_datasets:
                # Unpack dataset details; matched_participants will be empty if the dataset is from search_name
                name, path, readme_preview, *matched_participants = dataset
                
                # If no matched participants (from search_participant), set it to an empty list
                matched_participants = matched_participants[0] if matched_participants else []

                # Prepare the dataset name for display, falling back to the basename of the path if the name is empty
                name_to_display = name if name.strip() else os.path.basename(path)

                # Create and pack a label for the dataset name
                name_label = Label(self.bottom_frame, text=truncate_text(name_to_display, 100), anchor="w", justify="left", foreground="black", font=self.name_font)
                name_label.pack(pady=(10, 0), padx=5, anchor="w", fill="x")

                # Create and pack a label for the dataset path
                path_label = Label(self.bottom_frame, text=path, anchor="w", justify="left", foreground="green", font=self.path_font)
                path_label.pack(pady=(0, 0), padx=5, anchor="w", fill="x")

                # Create and pack a label for the README preview, truncating and inserting newlines as necessary
                readme_label = Label(self.bottom_frame, text=truncate_text(insert_newlines(readme_preview, 125), 500), anchor="w", justify="left", font=self.path_font)
                readme_label.pack(pady=(0, 2), padx=5, anchor="w", fill="x")

                # Display matched participant details, if any
                for participant_id, age, gender in matched_participants:
                    participant_info = f"Participant: {participant_id}"
                    if age is not None:
                        participant_info += f", Age: {age}"
                    if gender:
                        participant_info += f", Gender: {gender}"
                    participant_label = Label(self.bottom_frame, text=f"Participant: {participant_info}", anchor="w", justify="left", font=self.path_font)
                    participant_label.pack(pady=(0, 1), padx=5, anchor="w", fill="x")
        else:
            # If no datasets match, display a label indicating no results were found
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
        if new_path: 
            self.database_root = new_path
            self.database_path_display.config(text=self.database_root)