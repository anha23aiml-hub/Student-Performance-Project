import pandas as pd
from sklearn.model_selection import train_test_split

# Load ML dataset
df = pd.read_csv("data/ml/student_ml.csv")

# Separate features and target
X = df.drop("target", axis=1)
y = df["target"]

# First split: 70% training, 30% temporary
X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    random_state=42,
    stratify=y
)

# Second split: 15% validation, 15% test
X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    random_state=42,
    stratify=y_temp
)

print("Data split completed!")

print("Training data:", len(X_train))
print("Validation data:", len(X_val))
print("Test data:", len(X_test))

print("\nTotal:", len(X_train) + len(X_val) + len(X_test))