#model_training_initial_rf.py
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import matplotlib.pyplot as plt
import joblib

# Paths to the dataset files
TRAIN_FILE = r'C:\Users\adham\OneDrive - Carleton University\Desktop\Capstone\output\all_attacks_28features_preprocessed_cicids2017_train.csv'
TEST_FILE = r'C:\Users\adham\OneDrive - Carleton University\Desktop\Capstone\output\all_attacks_28features_preprocessed_cicids2017_test.csv'

# Ensure the files exist
if not os.path.exists(TRAIN_FILE):
    raise FileNotFoundError(f"Training file not found at: {TRAIN_FILE}")
if not os.path.exists(TEST_FILE):
    raise FileNotFoundError(f"Testing file not found at: {TEST_FILE}")

# Debug: Count rows in files
print(f"[DEBUG] Number of rows in training file: {sum(1 for line in open(TRAIN_FILE)) - 1}")
print(f"[DEBUG] Number of rows in testing file: {sum(1 for line in open(TEST_FILE)) - 1}")

# Load datasets
print("[INFO] Loading training and testing datasets...")
train_data = pd.read_csv(TRAIN_FILE)
test_data = pd.read_csv(TEST_FILE)

# Split features and target
X_train = train_data.drop(columns=['Attack'])
y_train = train_data['Attack']
X_test = test_data.drop(columns=['Attack'])
y_test = test_data['Attack']

# Debug: Check sizes of datasets
print(f"[DEBUG] Size of training dataset (features): {X_train.shape}")
print(f"[DEBUG] Size of training dataset (labels): {y_train.shape}")
print(f"[DEBUG] Size of testing dataset (features): {X_test.shape}")
print(f"[DEBUG] Size of testing dataset (labels): {y_test.shape}")

# Debug: Check for NaN values
print("[DEBUG] Checking for NaN values in training data...")
print(f"NaN values in X_train: {X_train.isnull().sum().sum()}")
print(f"NaN values in y_train: {y_train.isnull().sum()}")
print(f"NaN values in X_test: {X_test.isnull().sum().sum()}")
print(f"NaN values in y_test: {y_test.isnull().sum()}")

# Final duplicate check before model training
train_data_final = pd.concat([X_train, y_train], axis=1).drop_duplicates()
test_data_final = pd.concat([X_test, y_test], axis=1).drop_duplicates()
print(f"[INFO] Final training dataset after duplicate removal: {len(train_data_final)} rows.")
print(f"[INFO] Final testing dataset after duplicate removal: {len(test_data_final)} rows.")

# Train the Random Forest model
print("[INFO] Training Random Forest model on the entire training dataset...")
rf = RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=42, n_jobs=-1)
rf.fit(X_train, y_train)

# Make predictions
print("[INFO] Making predictions on the test set...")
y_pred = rf.predict(X_test)
y_proba = rf.predict_proba(X_test)[:, 1]

# Evaluate the model
print("[INFO] Evaluating Random Forest model...")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nConfusion Matrix:")
conf_matrix = confusion_matrix(y_test, y_pred)
print(conf_matrix)

# Calculate ROC-AUC Score
roc_auc = roc_auc_score(y_test, y_proba)
print("\nROC-AUC Score:", roc_auc)

# Plot ROC Curve
print("[INFO] Plotting ROC Curve...")
fpr, tpr, _ = roc_curve(y_test, y_proba)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f"Random Forest (AUC = {roc_auc:.2f})")
plt.plot([0, 1], [0, 1], 'k--', label="Random Guess")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.grid()
plt.tight_layout()

# Plot ROC Curve
print("[INFO] Plotting ROC Curve...")
fpr, tpr, _ = roc_curve(y_test, y_proba)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label="Random Forest (AUC = {:.2f})".format(roc_auc_score(y_test, y_proba)))
plt.plot([0, 1], [0, 1], 'k--', label="Random Guess")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.title("ROC Curve")
plt.legend()
plt.grid()
plt.tight_layout()

# Ensure the directory for saving the ROC curve exists
roc_curve_path = r'C:\Users\adham\OneDrive - Carleton University\Desktop\Capstone\Random_Forest_Model\all_attacks_rf_roc_curve_full.png'
roc_curve_dir = os.path.dirname(roc_curve_path)
os.makedirs(roc_curve_dir, exist_ok=True)

# Save and close the plot
plt.savefig(roc_curve_path)
plt.close()
print(f"[INFO] ROC Curve saved at {roc_curve_path}")

# Save model
print("[INFO] Saving Random Forest model trained on the full dataset...")
model_path = r'C:\Users\adham\OneDrive - Carleton University\Desktop\Capstone\Random_Forest_Model\all_attacks_random_forest_model_full.pkl'
joblib.dump(rf, model_path)
print(f"[INFO] Model saved at {model_path}")

# Program completed
print("[INFO] Program completed successfully.")
