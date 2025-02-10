#feature_selection.py

from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import matplotlib.pyplot as plt
import shap
from config import NUM_TOP_FEATURES, RANDOM_STATE
from utils import print_progress
from sklearn.feature_selection import mutual_info_classif
import seaborn as sns


def mi_feature_selection(X, y):
    """
    Computes feature importance using Mutual Information and prints and plots
    both all features and the top 20 features.

    Parameters:
    - X: pandas DataFrame, the feature matrix.
    - y: pandas Series or numpy array, the target vector.

    Returns:
    - top_20_mi_features: list of the top 20 feature names based on MI.
    """
    print_progress("Calculating Mutual Information for all features (Alternative Approach)...")

    # Compute mutual information scores for each feature
    mi_scores = mutual_info_classif(X, y, random_state=RANDOM_STATE)
    mi_importances = pd.Series(mi_scores, index=X.columns)
    mi_importances_sorted = mi_importances.sort_values(ascending=False)

    print("\n[INFO] Mutual Information Feature Importances (All Features):")
    for feature, importance in mi_importances_sorted.items():
        print(f"{feature}: {importance:.6f}")

    # Plot all features (MI)
    plt.figure(figsize=(12, 8))
    mi_importances_sorted.plot(kind='bar')
    plt.title('Mutual Information - All Features')
    plt.ylabel('Mutual Information Score')
    plt.xlabel('Features')
    plt.tight_layout()
    plt.savefig("mi_feature_importances_all.png")
    plt.close()
    print("[INFO] Mutual information (all features) plot saved as 'mi_feature_importances_all.png'.")

    # Select top 20 features based on MI
    top_20_mi = mi_importances_sorted.iloc[:NUM_TOP_FEATURES]

    print(f"\n[INFO] Top {NUM_TOP_FEATURES} Features by Mutual Information:")
    for feature, importance in top_20_mi.items():
        print(f"{feature}: {importance:.6f}")

    # Plot top 20 features (MI)
    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_20_mi.values, y=top_20_mi.index, orient='h')
    plt.title(f'Top {NUM_TOP_FEATURES} Features by Mutual Information (Alternative Approach)')
    plt.xlabel('Mutual Information Score')
    plt.ylabel('Features')
    plt.tight_layout()
    plt.savefig("mi_feature_importances_top20.png")
    plt.close()
    print(f"[INFO] Mutual information (top {NUM_TOP_FEATURES}) plot saved as 'mi_feature_importances_top20.png'.")

    return top_20_mi.index.tolist()


def generate_shap_summary_plot(model, X_full, top_features, filename='shap_summary_plot.png', top_n=20, max_samples=1000):
    """
    Generates a SHAP summary plot for feature contributions.

    Parameters:
    - model: Trained machine learning model (e.g., Random Forest).
    - X_full: Full scaled feature matrix (Pandas DataFrame) used for model training.
    - top_features: List of the top features to include in the SHAP calculation.
    - filename: Name of the file to save the SHAP plot.
    - top_n: Number of top features to display in the SHAP plot.
    - max_samples: Maximum number of samples to use for SHAP calculation.
    """
    print("[INFO] Generating SHAP summary plot...")

    # Restrict X to the top features only for SHAP calculation
    X_top = X_full[top_features]
    print(f"[INFO] Restricting dataset to the top {len(top_features)} features for SHAP calculation.")

    # Sample the data to a manageable size
    if len(X_top) > max_samples:
        print(f"[INFO] Sampling dataset to {max_samples} rows for SHAP calculation.")
        X_sampled = X_top.sample(n=max_samples, random_state=RANDOM_STATE)
    else:
        X_sampled = X_top

    print(f"[INFO] SHAP calculations will be performed on {len(X_sampled)} rows and {X_sampled.shape[1]} features.")

    # Check for NaN or Inf values
    print("[INFO] Checking for NaN or Inf values in the dataset...")
    if X_sampled.isnull().values.any():
        print("[ERROR] NaN values found in the dataset passed to SHAP.")
        print(X_sampled.isnull().sum())
        return
    if (X_sampled == float('inf')).values.any() or (X_sampled == float('-inf')).values.any():
        print("[ERROR] Inf values found in the dataset passed to SHAP.")
        return
    print("[INFO] No NaN or Inf values found in the dataset.")

    # Create SHAP explainer with additivity check disabled
    print("[INFO] Creating SHAP explainer with additivity check disabled...")
    explainer = shap.TreeExplainer(model, feature_perturbation="interventional")

    # Calculate SHAP values
    print("[INFO] Calculating SHAP values...")
    try:
        shap_values = explainer.shap_values(X_sampled, check_additivity=False)
        print("[INFO] SHAP values calculated successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to calculate SHAP values: {e}")
        return

    # For binary classification, select SHAP values for the positive class
    if isinstance(shap_values, list) and len(shap_values) == 2:
        shap_values = shap_values[1]

    # Ensure the SHAP values and X_sampled have the correct shapes
    if shap_values.shape[1] != X_sampled.shape[1]:
        print("[ERROR] SHAP values do not match the features in X_sampled.")
        print(f"SHAP values shape: {shap_values.shape}, X_sampled shape: {X_sampled.shape}")
        return

    # Generate summary plot using the same top features
    print("[INFO] Preparing to generate SHAP summary plot...")
    plt.figure(figsize=(12, len(top_features) * 0.5))
    try:
        shap.summary_plot(
            shap_values,  # SHAP values for the top features
            X_sampled,    # Use the same DataFrame for SHAP computation
            plot_type="dot",
            max_display=top_n,
            show=False
        )
        plt.savefig(filename, bbox_inches='tight')
        plt.close()
        print(f"[INFO] SHAP summary plot saved as '{filename}'.")
    except Exception as e:
        print(f"[ERROR] Failed to generate or save SHAP summary plot: {e}")


def rf_feature_selection(X, y):
    """
    Selects the top N features based on feature importance from a Random Forest classifier.

    Parameters:
    - X: pandas DataFrame, the feature matrix.
    - y: pandas Series or numpy array, the target vector.

    Returns:
    - X_top: pandas DataFrame, the feature matrix reduced to top N features.
    - top_features: list of the top N feature names based on Random Forest.
    """
    print_progress("Selecting top features using Random Forest...")

    # Initialize the Random Forest classifier
    rf = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE, n_jobs=-1)
    
    # Fit the model to the data
    rf.fit(X, y)
    
    # Extract feature importances
    feature_importances = pd.Series(rf.feature_importances_, index=X.columns)
    feature_importances_sorted = feature_importances.sort_values(ascending=False)

    print("\n[INFO] Random Forest Feature Importances (All Features):")
    for feature, importance in feature_importances_sorted.items():
        print(f"{feature}: {importance:.6f}")

    # Plot all features (RF)
    plt.figure(figsize=(12, 8))
    feature_importances_sorted.plot(kind='bar')
    plt.title('Random Forest - All Features')
    plt.ylabel('Feature Importance Score')
    plt.xlabel('Features')
    plt.tight_layout()
    plt.savefig("rf_feature_importances_all.png")
    plt.close()
    print("[INFO] Random Forest feature importances (all features) plot saved as 'rf_feature_importances_all.png'.")

    # Select the top N features
    top_20_rf = feature_importances_sorted.iloc[:NUM_TOP_FEATURES]

    print(f"\n[INFO] Top {NUM_TOP_FEATURES} Features by Random Forest:")
    for feature, importance in top_20_rf.items():
        print(f"{feature}: {importance:.6f}")

    # Plot top 20 features (RF)
    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_20_rf.values, y=top_20_rf.index, orient='h')
    plt.title(f'Top {NUM_TOP_FEATURES} Features by Random Forest')
    plt.xlabel('Feature Importance Score')
    plt.ylabel('Features')
    plt.tight_layout()
    plt.savefig("rf_feature_importances_top20.png")
    plt.close()
    print(f"[INFO] Random Forest feature importances (top {NUM_TOP_FEATURES}) plot saved as 'rf_feature_importances_top20.png'.")

    # # Generate SHAP summary plot for the Random Forest
    # generate_shap_summary_plot(
    #     model=rf,
    #     X_full=X,  # Use the full scaled dataset
    #     top_features=top_20_rf.index.tolist(),  # Restrict SHAP visualization to top features
    #     filename="shap_summary_plot_rf.png",
    #     top_n=NUM_TOP_FEATURES
    # )

    # Return the top features and the reduced feature matrix
    X_top = X[top_20_rf.index]
    return X_top, top_20_rf.index.tolist()