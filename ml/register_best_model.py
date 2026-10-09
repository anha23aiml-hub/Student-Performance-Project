
import os
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient

# Connect to MLflow
mlflow.set_tracking_uri("http://127.0.0.1:5000")
client = MlflowClient()

# Read model comparison report
comparison_file = "data/ml/mlflow_model_comparison.csv"

if not os.path.exists(comparison_file):
    raise FileNotFoundError(
        "Comparison report not found. "
        "Run ml/compare_mlflow_models.py first."
    )

comparison = pd.read_csv(comparison_file)

if comparison.empty or "F1 Score" not in comparison.columns:
    raise ValueError("The comparison report has no F1 Score data.")

# Select the model with the highest F1 score
best_row = comparison.loc[comparison["F1 Score"].idxmax()]
best_model_name = best_row["Model"]

print("Best model:", best_model_name)
print("F1 Score:", best_row["F1 Score"])

# Find experiment
experiment = client.get_experiment_by_name(
    "Student Performance Risk Prediction"
)

if experiment is None:
    raise ValueError("MLflow experiment not found.")

# Find completed runs with a logged model artifact
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    filter_string="attributes.status = 'FINISHED'",
    order_by=["attributes.start_time DESC"]
)

run_name_by_model = {
    "Logistic Regression": "Logistic Regression",
    "Random Forest": "Random Forest",
    "XGBoost": "XGBoost"
}

expected_run_name = run_name_by_model.get(best_model_name)

best_run = None

for run in runs:
    if run.data.tags.get("mlflow.runName") != expected_run_name:
        continue

    # Confirm the model artifact exists
    artifact_path = {
        "Logistic Regression": "logistic_regression_model",
        "Random Forest": "random_forest_model",
        "XGBoost": "xgboost_model"
    }[best_model_name]

    artifacts = client.list_artifacts(run.info.run_id, artifact_path)

    if artifacts:
        best_run = run
        break

if best_run is None:
    raise ValueError(
        "Could not find a completed run with a saved model for "
        + best_model_name
        + ". Run that model's MLflow training script successfully first."
    )

# Register the model
model_uri = (
    f"runs:/{best_run.info.run_id}/"
    f"{artifact_path}"
)

registered_model_name = "StudentPerformanceRiskModel"

result = mlflow.register_model(
    model_uri=model_uri,
    name=registered_model_name
)

print("\nModel registered successfully!")
print("Registered name:", result.name)
print("Model version:", result.version)
print("Source run ID:", best_run.info.run_id)