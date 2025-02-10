# data_loader.py

import os
import pandas as pd
from config import DATASET_DIR, CSV_FILES, LABEL_COLUMN
from utils import print_progress

def load_data():
    """
    Loads data from the CSV files specified in the configuration.
    Returns a concatenated pandas DataFrame.
    """
    data_list = []

    for idx, file_name in enumerate(CSV_FILES):
        file_path = os.path.join(DATASET_DIR, file_name)
        print_progress(f"Loading {file_name} ({idx + 1}/{len(CSV_FILES)})...")
        try:
            df = pd.read_csv(file_path, low_memory=False)
            data_list.append(df)
        except FileNotFoundError:
            print(f"Error: {file_name} not found in {DATASET_DIR}")
            continue

    if data_list:
        data = pd.concat(data_list, ignore_index=True)
        return data
    else:
        print("No data loaded. Please check the CSV files and paths.")
        return None
