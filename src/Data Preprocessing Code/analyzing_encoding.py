# this script helped me further analayze the encoding step because I felt that around 5K rows being removed from encoding is fishy
# because when I skimmed through the initial dataset myself I didn't see any label outside of the attack types included in the
# config file (so all the data was either BENGIN or 'DoS Hulk', 'DoS GoldenEye', 'DoS Slowloris', 'DoS Slowhttptest') so I created
# this script to print out the labels that were being removed which gave the output below:
# [INFO] Starting data acquisition and preprocessing...
# [INFO] Loading Wednesday-workingHours.pcap_ISCX.csv (1/1)...
# Initial dataset size: 692703 rows
# Labels excluded from the dataset: ['DoS slowloris', 'Heartbleed']
# Number of rows removed: 5807 (0.84% reduction)
# here we can see that 'DoS slowloris' was considered outside of the attack types while it should be inside just because of a difference
# in capitalization, so I fixed this bug by standardizing the labels and turning them to lowercase and removing any white space to avoid
# such a bug (and since 'Heartbleed' is not a DOS attack type its correct to remove it)
# after updatign the encoding method the output was as shown below:
# [INFO] Starting data acquisition and preprocessing...
# [INFO] Loading Wednesday-workingHours.pcap_ISCX.csv (1/1)...
# [INFO] Encoding labels and filtering attack types...
# Number of rows removed during encoding: 11 (0.00% reduction)
# which is great because initially there was around 5K of valid data being wrongly removed!

import pandas as pd
from config import LABEL_COLUMN, ATTACK_TYPES
import os
from data_loader import load_data
from data_preprocessing import preprocess_data, balance_data
from utils import print_progress
from config import OUTPUT_DIR, RANDOM_STATE

def test_encoding(data):
    """
    Tests the encoding step by identifying and printing values removed during filtering.
    """
    # Ensure the label column is properly named and strip any whitespace
    data.columns = data.columns.str.strip()
    data['Label'] = data['Label'].str.strip()

    # Initial size of the dataset
    initial_size = data.shape[0]
    print(f"Initial dataset size: {initial_size} rows")

    # Find labels that are not BENIGN or in the specified attack types
    excluded_labels = data.loc[~data['Label'].isin(['BENIGN'] + ATTACK_TYPES), 'Label'].unique()
    if excluded_labels.size > 0:
        print(f"Labels excluded from the dataset: {list(excluded_labels)}")
    else:
        print("No labels outside of BENIGN or specified attack types were found.")

    # Filter for specified attack types and benign traffic
    filtered_data = data.loc[data['Label'].isin(['BENIGN'] + ATTACK_TYPES)].copy()

    # Size after filtering
    final_size = filtered_data.shape[0]
    removed_rows = initial_size - final_size
    print(f"Number of rows removed: {removed_rows} ({(removed_rows / initial_size) * 100:.2f}% reduction)")

    return filtered_data

if __name__ == '__main__':
    print_progress("Starting data acquisition and preprocessing...")

    # Load data
    data = load_data()

    # Run the encoding test
    filtered_data = test_encoding(data)
