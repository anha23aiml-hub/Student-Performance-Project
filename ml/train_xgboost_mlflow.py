
import os
import pandas as pd
import mlflow
import mlflow.sklearn

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)
from xgboost import XGBClassifier

# 1. Load dataset
input_file = "data/ml/student_ml.csv"

if not os.path.exists(input_file):
    raise FileNotFoundError(
        f"Dataset not found: {input_file}"
    )

df = pd.read_csv(input_file)

if "target" not in df.columns:
    raise ValueError("The dataset must contain a target column.")

X = df.drop(columns=["target"])
y = df["target"].astype(int)

# 2. Identify column types
categorical_columns = X.select_dtypes(
    include=["object", "category", "bool"]
).columns.tolist()

numerical_columns = X.select_dtypes(
    include=["number"]
).columns.tolist()

# 3. Preprocess numerical data
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median"))
])

# 4. Preprocess categorical data
categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("num", numeric_pipeline, numerical_columns),
    ("cat", categorical_pipeline, categorical_columns)
])

# 5. Create XGBoost pipeline
model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        random_state=42,
        eval_metric="logloss"
    ))
])

# 6. Split data
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# 7. Connect to MLflow
mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("Student Performance Risk Prediction")

# 8. Train and track model
with mlflow.start_run(run_name="XGBoost"):

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

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

    # Record parameters
    mlflow.log_params({
        "model": "XGBoost",
        "n_estimators": 100,
        "max_depth": 4,
        "learning_rate": 0.1,
        "random_state": 42,
        "test_size": 0.20
    })

    # Record metrics
    mlflow.log_metrics({
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    })

    # Save trained model
    mlflow.sklearn.log_model(
        sk_model=model,
        name="xgboost_model",
        serialization_format="cloudpickle"
    )

    print("\nXGBoost trained successfully!")
    print("MLflow tracking completed successfully!")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")

    print("\nClassification Report:")
    print(classification_report(
        y_test, y_pred, zero_division=0
    ))