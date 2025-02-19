# main.py

import os
import pandas as pd
from data_loader import load_data
from data_preprocessing import preprocess_data, plot_class_distribution
from utils import print_progress
from config import OUTPUT_DIR, RANDOM_STATE
from imblearn.over_sampling import SMOTE

def remove_duplicates_after_feature_selection(X, y):
    """
    Removes duplicate rows from the feature set after feature selection and logs the number
    of attack rows removed.
    """
    print("[INFO] Removing duplicates after feature selection...")

    # Combine X and y for duplicate analysis
    combined_df = X.copy()
    combined_df['Attack'] = y

    # Count attack rows before deduplication
    attack_rows_before = combined_df['Attack'].sum()

    # Remove duplicates
    initial_rows = combined_df.shape[0]
    combined_df = combined_df.drop_duplicates()
    removed_rows = initial_rows - combined_df.shape[0]

    # Count attack rows after deduplication
    attack_rows_after = combined_df['Attack'].sum()

    # Calculate the number of attack rows removed
    attack_rows_removed = attack_rows_before - attack_rows_after

    print(f"[INFO] Removed {removed_rows} duplicate rows after feature selection "
          f"({(removed_rows / initial_rows) * 100:.2f}% reduction).")
    print(f"[INFO] Of these, {attack_rows_removed} rows were attacks.")

    # Separate X and y again
    X_deduplicated = combined_df.drop(columns=['Attack'])
    y_deduplicated = combined_df['Attack']

    return X_deduplicated, y_deduplicated

def balance_data_with_debug(X, y):
    """
    Balances the dataset using SMOTE and removes any duplicates that might be introduced.
    """
    print("[INFO] Balancing data with SMOTE...")
    smote = SMOTE(random_state=RANDOM_STATE)
    X_balanced, y_balanced = smote.fit_resample(X, y)

    # Debug: Check for duplicates before and after SMOTE
    print(f"[DEBUG] Number of duplicates before SMOTE: {X.duplicated().sum()}")
    print(f"[DEBUG] Number of samples after SMOTE: {X_balanced.shape[0]}")

    # Remove duplicates introduced by SMOTE
    df_balanced = pd.DataFrame(X_balanced, columns=X.columns)
    df_balanced['Attack'] = y_balanced
    duplicates_after_smote = df_balanced.duplicated().sum()
    print(f"[DEBUG] Number of duplicates after SMOTE: {duplicates_after_smote}")

    df_balanced = df_balanced.drop_duplicates()
    duplicates_removed = duplicates_after_smote - df_balanced.duplicated().sum()
    print(f"[DEBUG] Number of duplicates removed after SMOTE: {duplicates_removed}")

    X_balanced = df_balanced.drop(columns=['Attack'])
    y_balanced = df_balanced['Attack']
    print(f"[INFO] Dataset size after balancing and deduplication: {X_balanced.shape}")

    return X_balanced, y_balanced

def main():
    print_progress("Starting data acquisition and preprocessing...")

    # Load data
    data = load_data()
    if data is None:
        print("Data loading failed. Exiting.")
        return

    # Standardize column names to remove leading/trailing whitespace
    data.columns = data.columns.str.strip()

    # Debug: Check column names in the raw dataset
    # print("[DEBUG] Columns in the raw dataset after standardization:", data.columns)

    # Ensure the 'Label' column exists
    if 'Label' not in data.columns:
        raise KeyError("'Label' column not found in the dataset. Check the dataset for correctness.")

    # Visualize class distribution before feature selection
    plot_class_distribution(
        data['Label'], 
        'Class Distribution Before Feature Selection', 
        'class_distribution_before_feature_selection.png'
    )

    # Preprocess data and select top N features
    X_preprocessed, y = preprocess_data(data)

    # Debug: Check for NaN values before splitting
    # print("[DEBUG] Checking for NaN values before splitting:")
    # print(f"NaN values in X_preprocessed: {X_preprocessed.isnull().sum().sum()}")
    # print(f"NaN values in y: {y.isnull().sum()}")

    # Ensure alignment between X and y
    X_preprocessed = X_preprocessed.reset_index(drop=True)
    y = y.reset_index(drop=True)

    # Remove duplicates after feature selection
    X_preprocessed, y = remove_duplicates_after_feature_selection(X_preprocessed, y)

    # Split data into training and testing sets (20% testing and 80% training)
    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(
        X_preprocessed, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )

    # Debug: Check for NaN values after splitting
    # print("[DEBUG] Checking for NaN values after splitting:")
    # print(f"NaN values in X_train: {X_train.isnull().sum().sum()}")
    # print(f"NaN values in y_train: {y_train.isnull().sum()}")
    # print(f"NaN values in X_test: {X_test.isnull().sum().sum()}")
    # print(f"NaN values in y_test: {y_test.isnull()}")

    # Assert no NaN values are present
    assert not X_train.isnull().values.any(), "X_train contains NaN values!"
    assert not y_train.isnull().values.any(), "y_train contains NaN values!"
    assert not X_test.isnull().values.any(), "X_test contains NaN values!"
    assert not y_test.isnull().values.any(), "y_test contains NaN values!"

    # Visualize class distribution before SMOTE
    plot_class_distribution(
        y_train, 
        'Training Set Class Distribution Before SMOTE', 
        'class_distribution_before_smote.png'
    )

    # Balance only the training data
    X_train_balanced, y_train_balanced = balance_data_with_debug(X_train, y_train)

    # Visualize class distribution after SMOTE
    plot_class_distribution(
        y_train_balanced, 
        'Training Set Class Distribution After SMOTE', 
        'class_distribution_after_smote.png'
    )

    # Combine features and target for training data
    preprocessed_data_train = X_train_balanced.copy()
    preprocessed_data_train['Attack'] = y_train_balanced

    # Combine features and target for testing data
    preprocessed_data_test = X_test.copy()
    preprocessed_data_test['Attack'] = y_test

    # Debug: Check if the number of columns matches between train and test datasets
    print("[DEBUG] Checking the number of columns in train and test datasets:")
    print(f"Number of columns in training data: {preprocessed_data_train.shape[1]}")
    print(f"Number of columns in testing data: {preprocessed_data_test.shape[1]}")

    # Assert the number of columns match between train and test datasets
    assert preprocessed_data_train.shape[1] == preprocessed_data_test.shape[1], \
        "Mismatch in the number of columns between training and testing datasets!"

    # Save preprocessed training and testing data to CSV
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    output_file_train = os.path.join(OUTPUT_DIR, 'all_attacks_28features_preprocessed_cicids2017_train.csv')
    output_file_test = os.path.join(OUTPUT_DIR, 'all_attacks_28features_preprocessed_cicids2017_test.csv')

    preprocessed_data_train.to_csv(output_file_train, index=False)
    preprocessed_data_test.to_csv(output_file_test, index=False)

    print_progress(f"Cleaned and Preprocessed training data saved to {output_file_train}")
    print_progress(f"Cleaned testing data saved to {output_file_test}")
    print_progress("Data acquisition and preprocessing completed.")

if __name__ == '__main__':
    main()