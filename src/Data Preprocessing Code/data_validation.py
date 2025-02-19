import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

import matplotlib
matplotlib.use('Agg')  # Set backend to 'Agg' for environments without tkinter

# Load preprocessed data
data = pd.read_csv(r"C:\Users\adham\OneDrive - Carleton University\Desktop\Capstone\output\preprocessed_cicids2017.csv")

# 1. Check for Missing Values
print("Missing values per column:")
print(data.isnull().sum())
print("\n")

# 2. Check Data Types and Encoding
print("Data types of each column:")
print(data.dtypes)
print("\n")

# 3. Verify Feature Scaling and Distribution
print("Summary statistics:")
print(data.describe())
print("\n")

# 4. Inspect Class Distribution (for Binary Classification)
print("Class distribution of the target variable:")
print(data['Attack'].value_counts())
print("\n")

# 5. Check for Duplicate Rows
print("Number of duplicate rows:", data.duplicated().sum())
print("\n")

# 6. Validate Feature-Target Relationship with Correlation Heatmap
plt.figure(figsize=(12, 10))
sns.heatmap(data.corr(), annot=True, cmap="coolwarm", cbar=True)
plt.title("Correlation Heatmap")
plt.savefig("correlation_heatmap.png")  # Save plot instead of showing it
print("Correlation heatmap saved as 'correlation_heatmap.png'.")

# 7. Initial Model Testing (Sanity Check)
# Separate features and target
X = data.drop('Attack', axis=1)
y = data['Attack']

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a simple model (Logistic Regression)
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluate initial model accuracy
y_pred = model.predict(X_test)
print("Initial model accuracy:", accuracy_score(y_test, y_pred))
