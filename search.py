from bids.layout import BIDSLayout
import os
import json
import csv


def get_layout(bids_root):
    """
    Create and return a BIDSLayout object.
    """
    layout = BIDSLayout(bids_root)
    return layout

def get_all_datasets(database_root):
    """ Return a list of all datasets (full paths) in the given database root. """
    return [os.path.join(database_root, d) for d in os.listdir(database_root) if os.path.isdir(os.path.join(database_root, d))]

def get_readme_preview(dataset_dir):
    """ Return the first three non-empty lines of the README file in the dataset directory. """
    readme_path = os.path.join(dataset_dir, 'README')
    if os.path.exists(readme_path):
        with open(readme_path, 'r') as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]  # Filter out empty lines
            return '\n'.join(lines[:2])
    return ""


def search_name(database_root, keyword):
    if not keyword.strip():
        return []

    dataset_dirs = get_all_datasets(database_root)
    matching_datasets = []

    for dataset_dir in dataset_dirs:
        description_file = os.path.join(dataset_dir, 'dataset_description.json')
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                data = json.load(f)
                if keyword in data.get('Name', ''):
                    readme_preview = get_readme_preview(dataset_dir)
                    matching_datasets.append((data['Name'], dataset_dir, readme_preview))

    return matching_datasets


def search_participant(database_root, age_range=(0, 100), sex="all", no_filter=False):
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

                # Normalize column names
                normalized_columns = [col.lower() for col in reader.fieldnames]
                
                # Check for the sex/gender column and access original column name
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
                    # AGE FILTERING
                    if "age" in normalized_columns:
                        try:
                            age = int(row.get("age", 0))
                            # Only include participants within the age range
                            if not (age_range[0] <= age <= age_range[1]):
                                continue
                        except ValueError:
                            # Skip if age can't be converted to an int
                            continue

                    # SEX FILTERING
                    if sex_column_original and sex != "all":
                        participant_sex = row.get(sex_column_original, "").lower()
                        if (sex == "M" and participant_sex not in ["m", "male"]) or \
                           (sex == "F" and participant_sex not in ["f", "female"]) or \
                           (sex == "O" and participant_sex not in ["o", "other", "others"]):
                            continue

                    matched_participants.append((row["participant_id"], row.get("age")))

                # If any participants matched, store the dataset details
                if matched_participants:
                    description_file = os.path.join(dataset_dir, 'dataset_description.json')
                    with open(description_file, 'r') as f:
                        data = json.load(f)
                        readme_preview = get_readme_preview(dataset_dir)
                        matching_datasets.append((data['Name'], dataset_dir, readme_preview, matched_participants))

    return matching_datasets


def truncate_text(text, max_length):
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        else:
            return text

def insert_newlines(text, position=1):
    chunks = []
    while text:
        # If the remaining text is shorter than the position, just append it and break
        if len(text) <= position:
            chunks.append(text)
            break

        # Find the first space after the given position
        space_index = text.find(' ', position)

        # If there's no space after the position, take the entire remaining text
        if space_index == -1:
            chunks.append(text)
            break

        # Split the text at the found space and append the chunk
        chunks.append(text[:space_index])
        text = text[space_index+1:]  # Remaining text for next iteration

    return '\n'.join(chunks)