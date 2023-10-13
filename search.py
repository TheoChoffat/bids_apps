from bids.layout import BIDSLayout
import os
import json

def get_layout(bids_root):
    """
    Create and return a BIDSLayout object.
    """
    layout = BIDSLayout(bids_root)
    return layout

def get_all_datasets(database_root):
    """ Return a list of all datasets (full paths) in the given database root. """
    return [os.path.join(database_root, d) for d in os.listdir(database_root) if os.path.isdir(os.path.join(database_root, d))]

def search_in_description(database_root, keyword):
    dataset_dirs = get_all_datasets(database_root)
    matching_datasets = []

    for dataset_dir in dataset_dirs:
        description_file = os.path.join(dataset_dir, 'dataset_description.json')
        if os.path.exists(description_file):
            with open(description_file, 'r') as f:
                data = json.load(f)
                if keyword in data.get('Name', ''):
                    matching_datasets.append(data['Name'])
                if keyword in data.get('Authors', ''):
                    matching_datasets.append(data['Authors'])

    return matching_datasets
