
import os
import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

# 1. Load the ML dataset
input_file = "data/ml/student_ml.csv"

if not os.path.exists(input_file):
    raise FileNotFoundError(
        f"Dataset not found: {input_file}. "
        "Run ml/prepare_data.py first."
    )

df = pd.read_csv(input_file)

if "target" not in df.columns:
    raise ValueError("The dataset must contain a 'target' column.")

if df["target"].nunique() != 2:
    raise ValueError("The target must contain exactly two classes.")

# 2. Separate features and target
X = df.drop(columns=["target"])
y = df["target"].astype(int)

# 3. Identify categorical and numerical columns
categorical_columns = X.select_dtypes(
    include=["object", "category", "bool"]
).columns.tolist()

numerical_columns = X.select_dtypes(
    include=["number"]
).columns.tolist()

# 4. Preprocess numerical data
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler())
])

# 5. Preprocess categorical data
categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

# 6. Combine preprocessing
preprocessor = ColumnTransformer([
    ("num", numeric_pipeline, numerical_columns),
    ("cat", categorical_pipeline, categorical_columns)
])

# 7. Create Logistic Regression pipeline
model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(max_iter=1000))
])

# 8. Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# 9. Connect to the running MLflow server
mlflow.set_tracking_uri("http://127.0.0.1:5000")

mlflow.set_experiment("Student Performance Risk Prediction")

# 10. Train and track the experiment
with mlflow.start_run(run_name="Logistic Regression"):

    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Calculate evaluation metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(
        y_test, y_pred, zero_division=0
    )
    recall = recall_score(
        y_test, y_pred, zero_division=0
    )
    f1 = f1_score(
        y_test, y_pred, zero_division=0
    )

    # Record model parameters
    mlflow.log_params({
        "model": "Logistic Regression",
        "max_iter": 1000,
        "test_size": 0.20,
        "random_state": 42
    })

    # Record evaluation metrics
    mlflow.log_metrics({
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    })

    # Save the trained model in MLflow
    mlflow.sklearn.log_model(
        sk_model=model,
        name="logistic_regression_model",
        serialization_format="cloudpickle"
    )

    # Print results
    print("\nLogistic Regression trained successfully!")
    print("MLflow tracking completed successfully!")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        y_pred,
        zero_division=0
    ))