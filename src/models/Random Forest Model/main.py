#main

import pandas as pd
from config import TRAIN_FILE, TEST_FILE, IMPORTANCE_THRESHOLD, CORRELATION_THRESHOLD
from feature_engineering import (
    analyze_feature_importance,
    remove_low_importance_features,
    remove_highly_correlated_features,
    align_features,
)
from model_training_rf import train_and_evaluate_rf, plot_roc_curve_rf

# Define file paths for saving the preprocessed datasets
PROCESSED_TRAIN_FILE = "output/processed_train_data.csv"
PROCESSED_TEST_FILE = "output/processed_test_data.csv"

def log_duplicates(data, dataset_name, step_name):
    """
    Logs the number of duplicate rows in the dataset at a specific step.
    """
    duplicate_count = data.duplicated().sum()
    print(f"[INFO] {dataset_name} dataset after {step_name}: {duplicate_count} duplicate rows found out of {len(data)} total rows.")
    return duplicate_count

def main():
    print("[INFO] Loading training and testing datasets...")
    train_data = pd.read_csv(TRAIN_FILE)
    test_data = pd.read_csv(TEST_FILE)

    X_train = train_data.drop(columns=['Attack'])
    y_train = train_data['Attack']
    X_test = test_data.drop(columns=['Attack'])
    y_test = test_data['Attack']

    print(f"[DEBUG] Initial training dataset: {X_train.shape[1]} features")
    print(f"[DEBUG] Initial testing dataset: {X_test.shape[1]} features")

    # Log initial duplicates
    log_duplicates(pd.concat([X_train, y_train], axis=1), "Training", "initial load")
    log_duplicates(pd.concat([X_test, y_test], axis=1), "Testing", "initial load")

    # Analyze feature importance
    feature_importances = analyze_feature_importance(X_train, y_train)

    # Remove low-importance features
    X_train = remove_low_importance_features(X_train, IMPORTANCE_THRESHOLD, feature_importances)
    X_test = remove_low_importance_features(X_test, IMPORTANCE_THRESHOLD, feature_importances)

    # Log duplicates after low-importance feature removal
    log_duplicates(pd.concat([X_train, y_train], axis=1), "Training", "low-importance feature removal")
    log_duplicates(pd.concat([X_test, y_test], axis=1), "Testing", "low-importance feature removal")

    # Remove highly correlated features
    X_train = remove_highly_correlated_features(X_train, CORRELATION_THRESHOLD)
    X_test = remove_highly_correlated_features(X_test, CORRELATION_THRESHOLD)

    # Log duplicates after correlation-based feature removal
    log_duplicates(pd.concat([X_train, y_train], axis=1), "Training", "correlation-based feature removal")
    log_duplicates(pd.concat([X_test, y_test], axis=1), "Testing", "correlation-based feature removal")

    print(f"[DEBUG] Final training dataset: {X_train.shape[1]} features")
    print(f"[DEBUG] Final testing dataset: {X_test.shape[1]} features")

    # Align features between training and testing datasets
    X_train, X_test = align_features(X_train, X_test)

    # Final duplicate check and removal before model training
    train_data_final = pd.concat([X_train, y_train], axis=1).drop_duplicates()
    test_data_final = pd.concat([X_test, y_test], axis=1).drop_duplicates()
    print(f"[INFO] Final training dataset after duplicate removal: {len(train_data_final)} rows.")
    print(f"[INFO] Final testing dataset after duplicate removal: {len(test_data_final)} rows.")

    # **Save the processed datasets to CSV**
    train_data_final.to_csv(PROCESSED_TRAIN_FILE, index=False)
    test_data_final.to_csv(PROCESSED_TEST_FILE, index=False)
    print(f"[INFO] Processed training data saved to {PROCESSED_TRAIN_FILE}")
    print(f"[INFO] Processed testing data saved to {PROCESSED_TEST_FILE}")

    # Train and evaluate the Random Forest model
    model, y_proba = train_and_evaluate_rf(X_train, y_train, X_test, y_test)

    # Plot ROC curve
    plot_roc_curve_rf(y_test, y_proba)

    print("[INFO] Feature engineering and Random Forest model training completed.")

if __name__ == "__main__":
    main()
