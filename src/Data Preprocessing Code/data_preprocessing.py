# data_preprocessing.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from config import LABEL_COLUMN, ATTACK_TYPES, RANDOM_STATE
from feature_selection import rf_feature_selection, mi_feature_selection
from utils import print_progress
from sklearn.feature_selection import mutual_info_classif

def clean_data(data):
    """
    Cleans the data by handling missing values, duplicates, and standardizing column names.
    """
    print_progress("Cleaning data...")

    # Initial dataset size
    initial_shape = data.shape
    print(f"Initial dataset size: {initial_shape}")

    # Step 1: Remove columns with all missing values
    cols_before = data.shape[1]
    data.dropna(axis=1, how='all', inplace=True)
    cols_after = data.shape[1]
    cols_removed = cols_before - cols_after
    print(f"Step 1: Removed {cols_removed} columns with all missing values "
          f"({(cols_removed / cols_before) * 100:.2f}% reduction).")
    print(f"Dataset size after removing columns: {data.shape}")

    # Step 2: Remove duplicate rows
    rows_before = data.shape[0]
    data.drop_duplicates(inplace=True)
    rows_after = data.shape[0]
    rows_removed = rows_before - rows_after
    print(f"Step 2: Removed {rows_removed} duplicate rows "
          f"({(rows_removed / rows_before) * 100:.2f}% reduction).")
    print(f"Dataset size after removing duplicates: {data.shape}")

    # Step 3: Standardize column names and strip whitespace
    print("Step 3: Standardizing column names and stripping whitespace...")
    data.columns = data.columns.str.strip()
    data.columns = data.columns.str.replace(' ', '_')
    print(f"Dataset size after standardizing column names: {data.shape}")

    # Step 4: Strip whitespace from string columns
    print("Step 4: Stripping whitespace from string columns...")
    str_cols = data.select_dtypes(include=['object']).columns
    for col in str_cols:
        data[col] = data[col].str.strip()
    print(f"Dataset size after stripping whitespace: {data.shape}")

    # Step 5: Replace infinity values with NaN
    print("Step 5: Replacing infinity values with NaN...")
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    print(f"Dataset size after replacing infinity values: {data.shape}")

    # Step 6: Drop rows with NaN values
    rows_before = data.shape[0]
    data.dropna(inplace=True)
    rows_after = data.shape[0]
    rows_removed = rows_before - rows_after
    print(f"Step 6: Removed {rows_removed} rows with NaN values "
          f"({(rows_removed / rows_before) * 100:.2f}% reduction).")
    print(f"Dataset size after removing rows with NaN values: {data.shape}")

    # Final dataset size
    final_shape = data.shape
    print(f"Final dataset size: {final_shape}")
    reduction_rows = initial_shape[0] - final_shape[0]
    reduction_cols = initial_shape[1] - final_shape[1]
    print(f"Total reduction in rows: {reduction_rows} "
          f"({(reduction_rows / initial_shape[0]) * 100:.2f}% reduction).")
    print(f"Total reduction in columns: {reduction_cols} "
          f"({(reduction_cols / initial_shape[1]) * 100:.2f}% reduction).")

    return data

def encode_labels(data):
    """
    Encodes the labels into binary values (0 for benign, 1 for attack).
    Filters data for specified attack types and benign traffic.
    """
    print_progress("Encoding labels and filtering attack types...")

    # Ensure the label column is properly named and strip any whitespace
    data.columns = data.columns.str.strip()
    data[LABEL_COLUMN] = data[LABEL_COLUMN].str.strip()

    # Standardize labels to lowercase and strip any extra whitespace
    data[LABEL_COLUMN] = data[LABEL_COLUMN].str.lower().str.strip()

    # Standardize attack types to lowercase for comparison
    attack_types_lower = [attack.lower() for attack in ATTACK_TYPES]

    # Initial size of the dataset
    initial_size = data.shape[0]

    # Filter for specified attack types and benign traffic using .loc and .copy()
    data = data.loc[data[LABEL_COLUMN].isin(['benign'] + attack_types_lower)].copy()

    # Size after filtering
    final_size = data.shape[0]
    removed_rows = initial_size - final_size
    print(f"Number of rows removed during encoding: {removed_rows} "
          f"({(removed_rows / initial_size) * 100:.2f}% reduction)")

    # Create a new binary target column
    data['Attack'] = data[LABEL_COLUMN].apply(lambda x: 0 if x == 'benign' else 1)

    # Drop the original Label column
    data.drop(columns=[LABEL_COLUMN], inplace=True)

    return data

def scale_features(X):
    """
    Scales numerical features using StandardScaler.
    """
    print_progress("Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return X_scaled

def plot_class_distribution(y, title, filename):
    """
    Plots the class distribution for the target variable.

    Parameters:
    - y: pandas Series or numpy array, the target variable.
    - title: str, the title of the plot.
    - filename: str, the filename to save the plot.
    """
    plt.figure(figsize=(8, 6)) 
    sns.countplot(x=y)  # Plot the class distribution
    plt.title(title)
    plt.xlabel('Class')  # Use 'Class' for binary classification (0 and 1)
    plt.ylabel('Count')  # The count of samples in each class
    plt.xticks([0, 1], ['Benign', 'Attack'])  # Label the x-axis categories
    plt.tight_layout()  # Ensuring everything fits in the figure
    plt.savefig(filename)
    plt.close()


def balance_data(X, y):
    """
    Handles class imbalance using SMOTE and prints dataset size after balancing.
    """
    print_progress("Balancing data with SMOTE...")
    smote = SMOTE(random_state=RANDOM_STATE)
    X_resampled, y_resampled = smote.fit_resample(X, y)
    
    # Print size after SMOTE balancing
    print(f"Dataset size after balancing with SMOTE: {X_resampled.shape}")
    
    # Convert resampled features to a DataFrame for easier processing
    X_resampled = pd.DataFrame(X_resampled, columns=X.columns)
    
    # Combine X and y for easier handling of duplicates
    balanced_data = X_resampled.copy()
    balanced_data['Attack'] = y_resampled
    
    # Remove duplicates
    num_duplicates_before = balanced_data.duplicated().sum()
    balanced_data.drop_duplicates(inplace=True)
    num_duplicates_after = balanced_data.duplicated().sum()
    
    # Print size after removing duplicates
    print(f"Duplicates before removing: {num_duplicates_before}")
    print(f"Duplicates after removing: {num_duplicates_after}")
    print(f"Dataset size after removing duplicates: {balanced_data.shape}")
    
    # Separate features and target after duplicate removal
    X_final = balanced_data.drop(columns=['Attack'])
    y_final = balanced_data['Attack']
    
    return X_final, y_final

def preprocess_data(data):
    """
    Orchestrates the preprocessing steps.
    
    Parameters:
    - data: pandas DataFrame, the raw data loaded from CSV.
    
    Returns:
    - X_selected: pandas DataFrame, preprocessed feature matrix with top N features (from Random Forest).
    - y: pandas Series, the target vector.
    """
    print_progress(f"Initial data size: {data.shape}")
    
    data = clean_data(data)
    print_progress(f"Data size after cleaning: {data.shape}")
    
    data = encode_labels(data)
    print_progress(f"Data size after encoding labels: {data.shape}")
    
    X = data.drop(columns=['Attack'])
    y = data['Attack']
    
    X = X.apply(pd.to_numeric, errors='coerce')
    X.fillna(0, inplace=True)
    
    X_scaled = scale_features(X)
    feature_names = X.columns
    X_scaled = pd.DataFrame(X_scaled, columns=feature_names)
    
    # Call MI-based feature selection (for comparison only)
    # top_20_mi_features = mi_feature_selection(X_scaled, y)
    
    # Now call the original Random Forest-based feature selection
    X_selected, top_features = rf_feature_selection(X_scaled, y)
    
    return X_selected, y
