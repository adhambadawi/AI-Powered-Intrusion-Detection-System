import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, cross_validate
from sklearn.metrics import make_scorer, roc_auc_score, f1_score, classification_report
from config import TRAIN_FILE, TEST_FILE

# Load the dataset
train_data = pd.read_csv(TRAIN_FILE)

# Split features and target
X_train = train_data.drop(columns=['Attack'])
y_train = train_data['Attack']

# Define the Random Forest model
rf = RandomForestClassifier(
    n_estimators=100,
    class_weight="balanced",
    random_state=42,
    n_jobs=-1
)

# Define metrics for cross-validation
scoring = ['roc_auc', 'f1']

# Perform 5-Fold Cross-Validation
print("[INFO] Performing 5-Fold Cross-Validation...")
cv_results = cross_validate(
    rf, X_train, y_train, cv=5, scoring=scoring, return_train_score=True, n_jobs=-1
)

# Output Cross-Validation Results
print("\n[INFO] Cross-Validation Results:")
print(f"Train ROC-AUC: {cv_results['train_roc_auc'].mean():.4f} ± {cv_results['train_roc_auc'].std():.4f}")
print(f"Validation ROC-AUC: {cv_results['test_roc_auc'].mean():.4f} ± {cv_results['test_roc_auc'].std():.4f}")
print(f"Train F1-Score: {cv_results['train_f1'].mean():.4f} ± {cv_results['train_f1'].std():.4f}")
print(f"Validation F1-Score: {cv_results['test_f1'].mean():.4f} ± {cv_results['test_f1'].std():.4f}")
