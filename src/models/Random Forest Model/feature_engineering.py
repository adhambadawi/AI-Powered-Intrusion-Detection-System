#feature_engineering.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.ensemble import RandomForestClassifier

def analyze_feature_importance(X_train, y_train):
    print("[INFO] Analyzing feature importance using Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_train, y_train)

    feature_importances = pd.Series(rf.feature_importances_, index=X_train.columns).sort_values(ascending=False)
    print("[DEBUG] Top 28 Features by Importance:")
    print(feature_importances.head(28))

    # Ensure the output directory exists
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)

    # Save and plot feature importance
    feature_importances.head(28).plot(kind='bar', figsize=(10, 6), title="Top 28 Feature Importances")
    plt.tight_layout()
    plot_path = os.path.join(output_dir, 'feature_importances.png')
    plt.savefig(plot_path)
    plt.close()
    print(f"[INFO] Feature importance plot saved as '{plot_path}'.")

    return feature_importances

def remove_low_importance_features(X, importance_threshold, feature_importances):
    print(f"[INFO] Removing features with importance below {importance_threshold}...")
    low_importance_features = feature_importances[feature_importances < importance_threshold].index.tolist()

    if low_importance_features:
        print(f"[DEBUG] Features removed due to low importance (Importance < {importance_threshold}):")
        for feature in low_importance_features:
            print(f"{feature}: {feature_importances[feature]:.6f}")
        X_reduced = X.drop(columns=low_importance_features)
        print(f"[INFO] Reduced feature set: {X_reduced.shape[1]} features remaining (from {X.shape[1]}).")
    else:
        print("[INFO] No features removed due to low importance.")
        X_reduced = X

    return X_reduced

def remove_highly_correlated_features(X, correlation_threshold):
    print(f"[INFO] Removing features with correlation greater than {correlation_threshold}...")
    corr_matrix = X.corr().abs()
    upper_triangle = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    highly_correlated = [column for column in upper_triangle.columns if any(upper_triangle[column] > correlation_threshold)]

    if highly_correlated:
        print("[DEBUG] Features removed due to high correlation:")
        for feature in highly_correlated:
            correlated_with = upper_triangle[feature][upper_triangle[feature] > correlation_threshold].index.tolist()
            print(f"{feature}: Correlated with {correlated_with}")
        X_reduced = X.drop(columns=highly_correlated)
        print(f"[INFO] Reduced feature set: {X_reduced.shape[1]} features remaining (from {X.shape[1]}).")
    else:
        print("[INFO] No features removed due to high correlation.")
        X_reduced = X

    return X_reduced

def align_features(X_train, X_test):
    """
    Ensures that both training and testing datasets have the same feature columns.
    Extra features in one dataset are dropped, and missing features are added with default values.

    Parameters:
    - X_train: pandas DataFrame, the training dataset.
    - X_test: pandas DataFrame, the testing dataset.

    Returns:
    - Aligned training and testing datasets.
    """
    print("[INFO] Aligning features between training and testing datasets...")
    
    # Get common and unique columns
    train_features = set(X_train.columns)
    test_features = set(X_test.columns)
    
    missing_in_test = train_features - test_features
    missing_in_train = test_features - train_features

    # Add missing columns to testing dataset with default value of 0
    for col in missing_in_test:
        X_test[col] = 0
        print(f"[DEBUG] Adding missing feature to testing dataset: {col} (default=0)")

    # Add missing columns to training dataset with default value of 0
    for col in missing_in_train:
        X_train[col] = 0
        print(f"[DEBUG] Adding missing feature to training dataset: {col} (default=0)")

    # Reorder columns to match
    X_test = X_test[X_train.columns]

    print(f"[INFO] Feature alignment completed. Training dataset: {X_train.shape[1]} features, Testing dataset: {X_test.shape[1]} features.")
    return X_train, X_test
