import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import time
import tracemalloc
from sklearn.model_selection import train_test_split, cross_val_score, learning_curve, KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score, 
                             roc_auc_score, confusion_matrix, roc_curve)

# =============================================================================
# 1. DATA DESCRIPTION & PROBLEM STATEMENT
# =============================================================================
# Problem: Predict student academic Pass/Fail status based on academic and personal attributes.
# Task Type: Supervised Binary Classification.
# Dataset: Records of 500 students (Source: Kaggle Synthetic).

# Start tracking computational cost
tracemalloc.start()
start_time = time.time()

# =============================================================================
# 2. DATA PREPROCESSING
# =============================================================================
print("--- Step 2: Data Preprocessing ---")
try:
    df = pd.read_csv('student-mat.csv')
except FileNotFoundError:
    print("Error: student-mat.csv not found.")
    exit()

# Target Variable Derivation: Pass if FinalGrade >= 50, else Fail
df['Result'] = df['FinalGrade'].apply(lambda x: 1 if x >= 50 else 0)

# Feature Encoding
le = LabelEncoder()
df['Gender'] = le.fit_transform(df['Gender'])
df['ParentalSupport'] = le.fit_transform(df['ParentalSupport'])

# Define Features and Target
X = df.drop(['StudentID', 'Name', 'FinalGrade', 'Result'], axis=1)
y = df['Result']

# Train/Test Split (80/20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Feature Scaling
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# =============================================================================
# 3. MODEL SELECTION & JUSTIFICATION
# =============================================================================
# Chosen Algorithm: Random Forest Classifier
# Justification: 
# - Handles non-linear relationships well.
# - Reduces overfitting via ensemble averaging (bagging).
# - Robust to outliers and missing data.
# - Theoretical background: Ensemble of Decision Trees with feature bagging.

model = RandomForestClassifier(n_estimators=100, max_depth=None, random_state=42)
model.fit(X_train, y_train)

# =============================================================================
# 4. CROSS-VALIDATION (K=5)
# =============================================================================
print("\n--- Step 4: K-Fold Cross-Validation ---")
kf = KFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train, y_train, cv=kf)
print(f"Mean CV Score: {cv_scores.mean():.4f}")
print(f"Standard Deviation: {cv_scores.std():.4f}")

# =============================================================================
# 5. OVERFITTING VS UNDERFITTING (Learning Curves)
# =============================================================================
print("\n--- Step 5: Diagnosing Overfitting/Underfitting ---")
train_sizes, train_scores, valid_scores = learning_curve(
    model, X_train, y_train, train_sizes=np.linspace(0.1, 1.0, 5), cv=kf)

plt.figure(figsize=(10, 6))
plt.plot(train_sizes, np.mean(train_scores, axis=1), 'o-', label="Training Score")
plt.plot(train_sizes, np.mean(valid_scores, axis=1), 'o-', label="Cross-validation Score")
plt.title("Learning Curves (Random Forest)")
plt.xlabel("Training Examples")
plt.ylabel("Score")
plt.legend(loc="best")
plt.grid()
plt.savefig('learning_curves.png')
print("Learning curves saved to learning_curves.png")

# =============================================================================
# 6. EVALUATION METRICS
# =============================================================================
print("\n--- Step 6: Evaluation Metrics ---")
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

metrics = {
    "Accuracy": accuracy_score(y_test, y_pred),
    "Precision": precision_score(y_test, y_pred),
    "Recall": recall_score(y_test, y_pred),
    "F1-Score": f1_score(y_test, y_pred),
    "ROC-AUC": roc_auc_score(y_test, y_prob)
}

for m, v in metrics.items():
    print(f"{m}: {v:.4f}")

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Fail', 'Pass'], yticklabels=['Fail', 'Pass'])
plt.title("Confusion Matrix")
plt.ylabel('True label')
plt.xlabel('Predicted label')
plt.savefig('confusion_matrix.png')

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_prob)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f"ROC-AUC = {metrics['ROC-AUC']:.4f}")
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
plt.savefig('roc_curve.png')

# =============================================================================
# 7. COMPUTATIONAL COST ANALYSIS
# =============================================================================
end_time = time.time()
training_time = end_time - start_time
current_mem, peak_mem = tracemalloc.get_traced_memory()
tracemalloc.stop()

# Prediction time per sample
start_pred = time.time()
model.predict(X_test[:1])
pred_time_per_sample = time.time() - start_pred

with open('computational_cost_report.txt', 'w') as f:
    f.write("COMPUTATIONAL COST ANALYSIS\n")
    f.write("-" * 30 + "\n")
    f.write(f"Total Workflow Time (s): {training_time:.4f}\n")
    f.write(f"Peak Memory Usage (MB): {peak_mem / 10**6:.4f}\n")
    f.write(f"Prediction Time per Sample (s): {pred_time_per_sample:.4f}\n")

print(f"\n--- Step 7: Computational Cost ---")
print(f"Total Time: {training_time:.4f}s")
print(f"Peak Memory: {peak_mem / 10**6:.4f} MB")
print("Full report saved to computational_cost_report.txt")