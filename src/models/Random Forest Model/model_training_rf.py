#model_training_rf.py
import os
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import joblib

def train_and_evaluate_rf(X_train, y_train, X_test, y_test):
    # Train the Random Forest model
    print("[INFO] Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # Predictions
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Evaluation
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    print("\nConfusion Matrix:")
    conf_matrix = confusion_matrix(y_test, y_pred)
    print(conf_matrix)

    roc_auc = roc_auc_score(y_test, y_proba)
    print("\nROC-AUC Score:", roc_auc)

    # Save the model
    model_path = 'output/all_attacks_random_forest_model.pkl'
    joblib.dump(model, model_path)
    print(f"[INFO] Random Forest model saved at {model_path}")

    return model, y_proba

def plot_roc_curve_rf(y_test, y_proba):
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f"Random Forest (AUC = {roc_auc_score(y_test, y_proba):.2f})")
    plt.plot([0, 1], [0, 1], 'k--', label="Random Guess")
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve - Random Forest")
    plt.legend()
    plt.tight_layout()
    plot_path = 'output/all_attacks_rf_roc_curve.png'
    plt.savefig(plot_path)
    plt.close()
    print(f"[INFO] ROC Curve saved at {plot_path}")
