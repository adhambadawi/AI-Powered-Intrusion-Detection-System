# data_validation_and_modeling.py

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Set backend to 'Agg' for environments without tkinter
matplotlib.use('Agg')  

# Load preprocessed data
data = pd.read_csv(r"C:\Users\adham\OneDrive - Carleton University\Desktop\Capstone\output\preprocessed_cicids2017.csv")

# After the first run, we had 26672 duplicate rows, so we're removing them here to avoid redundancy and increase model accuracy
# 1. Remove Duplicate Rows
print("Number of duplicate rows before removing:", data.duplicated().sum())
data = data.drop_duplicates()
print("Number of duplicate rows after removing:", data.duplicated().sum())
print("\n")

# 2. Check for Missing Values
print("Missing values per column:")
print(data.isnull().sum())
print("\n")

# 3. Check Data Types and Encoding
print("Data types of each column:")
print(data.dtypes)
print("\n")

# 4. Verify Feature Scaling and Distribution
print("Summary statistics:")
print(data.describe())
print("\n")

# 5. Inspect Class Distribution (for Binary Classification)
print("Class distribution of the target variable:")
print(data['Attack'].value_counts())
print("\n")

# In our initial validation test we had some features that were highly correlated, so to reduce multicollinearity, we'll remove one feature from each pair of features with a high correlation coefficient (e.g., greater than 0.95).
# 6. Remove Highly Correlated Features
# Calculate the correlation matrix
corr_matrix = data.corr().abs()

# Select the upper triangle of the correlation matrix
upper_triangle = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))

# Identify features with correlation greater than 0.95
high_correlation_threshold = 0.95
to_drop = [column for column in upper_triangle.columns if any(upper_triangle[column] > high_correlation_threshold)]

print("Highly correlated features to drop:", to_drop)

# Drop highly correlated features
data = data.drop(columns=to_drop)

# Save cleaned and reduced data back to the CSV file
cleaned_data_path = r"C:\Users\adham\OneDrive - Carleton University\Desktop\Capstone\output\preprocessed_cicids2017_train.csv"
data.to_csv(cleaned_data_path, index=False)
print(f"Cleaned data saved to {cleaned_data_path}")

# 7. Validate and Visualize the Correlation Matrix
plt.figure(figsize=(12, 10))
sns.heatmap(data.corr(), annot=True, cmap="coolwarm", cbar=True)
plt.title("Correlation Heatmap After Removing Highly Correlated Features")
plt.savefig("correlation_heatmap_after.png")
print("Correlation heatmap after removing highly correlated features saved as 'correlation_heatmap_after.png'.")
print("\n")

# 8. Retrain and Evaluate the Model
# Separate features and target variable
X = data.drop('Attack', axis=1)
y = data['Attack']

# Split data into training and test sets
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model (Logistic Regression)
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluate the model
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

y_pred = model.predict(X_test)

print("Model accuracy after preprocessing:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
