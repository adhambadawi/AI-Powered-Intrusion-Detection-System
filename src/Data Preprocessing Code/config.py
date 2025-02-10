# config.py

import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Output directory for preprocessed data
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')

# Dataset directory
DATASET_DIR = os.path.join(
    BASE_DIR,
    'Dataset',
    'MachineLearningCSV',
    'MachineLearningCVE'
)

# List of all CSV files in the dataset
CSV_FILES = [
    'Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv',
    'Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv',
    'Friday-WorkingHours-Morning.pcap_ISCX.csv',
    'Monday-WorkingHours.pcap_ISCX.csv',
    'Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv',
    'Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv',
    'Tuesday-WorkingHours.pcap_ISCX.csv',
    'Wednesday-workingHours.pcap_ISCX.csv'
]

# Focus on all attack types for binary classification
ATTACK_TYPES = [
    'DoS Hulk', 'DoS GoldenEye', 'DoS Slowloris', 'DoS slowloris', 'DoS Slowhttptest', 'Heartbleed',
    'Web Attack - Brute Force', 'Web Attack - XSS', 'Web Attack - Sql Injection',
    'Infiltration', 'Bot', 'PortScan', 'DDoS', 'FTP-Patator', 'SSH-Patator'
]

# Column name for labels (adjust if necessary)
LABEL_COLUMN = 'Label'


# Route to choose optimal N:
# 1. Trade-Off Between Attack Row Retention and Model Complexity:
# * From N=20N = 20N=20 to N=26N = 26N=26, significant numbers of attack rows are removed, which could harm model performance in detecting rare attack types.
# * Beyond N=27N = 27N=27, the attack row retention is excellent, and data loss due to duplicates is minimal.
# 2. Dataset Size and Model Complexity:
# * The dataset size peaks at N=28N = 28N=28 to N=30N = 30N=30, providing ample training data.
# * Beyond N=30N = 30N=30, the marginal increase in features adds complexity without significant benefit.
# 3. Balance Between Retention and Generalization:
# * N=28N = 28N=28 offers excellent retention of attack rows (8,394 removed) and a balanced dataset size of 3.25M rows.
# * N=29N = 29N=29 and N=30N = 30N=30 provide slightly larger datasets but no meaningful improvement over N=28.

# Number of top features to select 
NUM_TOP_FEATURES = 28

# Random seed for reproducibility
RANDOM_STATE = 42
