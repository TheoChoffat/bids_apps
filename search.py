from bids.layout import BIDSLayout
import os
import json
import csv


def get_layout(bids_root):
    '''
    Initialize and return a BIDSLayout object for a given BIDS dataset root.
    
    Parameters:
    bids_root: Path to the root of the BIDS dataset.
    
    Returns:
    BIDSLayout object.
    '''
    return BIDSLayout(bids_root)

def get_all_datasets(database_root):
    '''
    Retrieve all dataset directories within the specified database root.
    
    Parameters:
    database_root: Path to the root directory containing multiple datasets.
    
    Returns:
    List of paths to dataset directories.
    '''
    return [
        os.path.join(database_root, d) 
        for d in os.listdir(database_root) 
        if os.path.isdir(os.path.join(database_root, d))
    ]

def get_readme_preview(dataset_dir):
    '''
    Extract and return the first two non-empty lines from the README file in a dataset directory.
    
    Parameters:
    dataset_dir: Path to the dataset directory.
    
    Returns:
    String containing the first two lines of the README file, or empty string if not found.
    '''
    readme_path = os.path.join(dataset_dir, 'README')
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]  
            return '\n'.join(lines[:2])
    return ""


def search_name(database_root, keyword):
    '''
    Search for datasets by name keyword in the specified database root and return matching datasets.
    
    Parameters:
    database_root - Path to the root directory containing multiple datasets.
    keyword - Keyword to search for in dataset names and README files.
    
    Returns:
    List of tuples containing dataset names and their directory paths for all matching datasets.
    '''
    if not keyword.strip():
        return []

    dataset_dirs = get_all_datasets(database_root)
    matching_datasets = []

    for dataset_dir in dataset_dirs:
        description_file = os.path.join(dataset_dir, 'dataset_description.json')
        readme_file = os.path.join(dataset_dir, 'README')
        match_found = False
        dataset_name = ""
        
        # Check if keyword is in the dataset name
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                data = json.load(f)
                if keyword in data.get('Name', ''):
                    dataset_name = data['Name']
                    match_found = True

        # Check if keyword is in the README file
        if os.path.exists(readme_file):
            with open(readme_file, 'r') as f:
                readme_content = f.read()
                if keyword in readme_content:
                    if not match_found and os.path.exists(description_file):
                        with open(description_file, 'r') as f:
                            data = json.load(f)
                            dataset_name = data.get('Name', 'Unnamed Dataset')
                    match_found = True

        if match_found:
            readme_preview = get_readme_preview(dataset_dir)
            matching_datasets.append((dataset_name, dataset_dir, readme_preview))

    return matching_datasets


def search_participant(database_root, age_range=(0, 100), sex="all", no_filter=False):
    '''
    Search for participants within the specified database root based on age and sex, and return matching datasets.
    
    Parameters:
    - database_root: Path to the root directory containing multiple datasets.
    - age: Age of the participant to search for.
    - sex: Sex of the participant to search for.
    
    Returns:
    - List of tuples containing dataset directory paths and the list of matching participant IDs.
    '''
    dataset_dirs = get_all_datasets(database_root)
    matching_datasets = []

    for dataset_dir in dataset_dirs:
        participants_file = os.path.join(dataset_dir, 'participants.tsv')
        if no_filter and not os.path.exists(participants_file):
            description_file = os.path.join(dataset_dir, 'dataset_description.json')
            with open(description_file, 'r') as f:
                data = json.load(f)
                readme_preview = get_readme_preview(dataset_dir)
                matching_datasets.append((data['Name'], dataset_dir, readme_preview))
            continue

        elif os.path.exists(participants_file):
            with open(participants_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter='\t')
                matched_participants = []
                normalized_columns = [col.lower() for col in reader.fieldnames]
                sex_column = None
                
                if "sex" in normalized_columns:
                    sex_column = "sex"     
                elif "gender" in normalized_columns:
                    sex_column = "gender"
                    
                if sex_column:
                    sex_column_original = next((col for col in reader.fieldnames if col.lower() == sex_column), None)

                if "age" not in normalized_columns and age_range != (0, 100):
                    continue  

                for row in reader:
                    if "age" in normalized_columns:
                        try:
                            age = int(row.get("age", 0))
                            if not (age_range[0] <= age <= age_range[1]):
                                continue
                        except ValueError:
                            continue

                    if sex_column_original and sex != "all":
                        participant_sex = row.get(sex_column_original, "").lower()
                        if (sex == "M" and participant_sex not in ["m", "male"]) or \
                           (sex == "F" and participant_sex not in ["f", "female"]) or \
                           (sex == "O" and participant_sex not in ["o", "other", "others"]):
                            continue
                    
                    gender = row.get(sex_column_original, "") if sex_column_original else None
                    matched_participants.append((row["participant_id"], row.get("age"), gender))
               
                if matched_participants:
                    description_file = os.path.join(dataset_dir, 'dataset_description.json')
                    with open(description_file, 'r') as f:
                        data = json.load(f)
                        readme_preview = get_readme_preview(dataset_dir)
                        matching_datasets.append((data['Name'], dataset_dir, readme_preview, matched_participants))

    return matching_datasets


def truncate_text(text, max_length):
    '''
    Truncate a given text to a specified maximum length, adding ellipsis if truncated.
    
    Parameters:
    text - The text to be truncated.
    max_length - The maximum allowed length of the text.
    
    Returns:
    Truncated text with ellipsis (...) if the original text exceeds max_length.
    '''
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    else:
        return text

def insert_newlines(text, position=1):
    '''
    Insert newlines into a text at specified positions, breaking at spaces.
    
    Parameters:
    text - The text to be processed.
    position - The position (number of characters) at which to insert a newline.
    
    Returns:
    Text with newlines inserted.
    '''
    chunks = []
    while text:
        if len(text) <= position:
            chunks.append(text)
            break

        space_index = text.find(' ', position)

        if space_index == -1:
            chunks.append(text)
            break

        chunks.append(text[:space_index])
        text = text[space_index+1:]  
        
    return '\n'.join(chunks)