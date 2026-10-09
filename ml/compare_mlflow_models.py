
import mlflow
import pandas as pd

# Connect to MLflow
mlflow.set_tracking_uri("http://127.0.0.1:5000")

experiment_name = "Student Performance Risk Prediction"

# Find the experiment
experiment = mlflow.get_experiment_by_name(experiment_name)

if experiment is None:
    raise ValueError(
        "Experiment not found. Run the model training scripts first."
    )

# Get all runs from this experiment
runs = mlflow.search_runs(
    experiment_ids=[experiment.experiment_id],
    output_format="pandas"
)

if runs.empty:
    raise ValueError(
        "No experiment runs found. Train the models first."
    )

# Keep only the three model runs
runs = runs[
    runs["tags.mlflow.runName"].isin([
        "Logistic Regression",
        "Random Forest",
        "XGBoost"
    ])
].copy()

# Check that the metrics exist
required_metrics = [
    "metrics.accuracy",
    "metrics.precision",
    "metrics.recall",
    "metrics.f1_score"
]

available_metrics = [
    column for column in required_metrics if column in runs.columns
]

if "tags.mlflow.runName" not in runs.columns or not available_metrics:
    raise ValueError(
        "Required model names or metrics were not found in MLflow."
    )

# Prepare comparison table
comparison = runs[
    ["tags.mlflow.runName"] + available_metrics
].copy()

comparison = comparison.rename(columns={
    "tags.mlflow.runName": "Model",
    "metrics.accuracy": "Accuracy",
    "metrics.precision": "Precision",
    "metrics.recall": "Recall",
    "metrics.f1_score": "F1 Score"
})

# Show the latest run for each model
comparison = comparison.drop_duplicates(
    subset=["Model"],
    keep="first"
)

# Sort by F1 score
if "F1 Score" in comparison.columns:
    comparison = comparison.sort_values(
        by="F1 Score",
        ascending=False
    )

print("\n===== MLflow Model Comparison =====")
print(comparison.to_string(index=False))

# Save the report
comparison.to_csv(
    "data/ml/mlflow_model_comparison.csv",
    index=False
)

print("\nComparison saved to:")
print("data/ml/mlflow_model_comparison.csv")

if "F1 Score" in comparison.columns and not comparison.empty:
    best = comparison.iloc[0]
    print("\nBest model by F1 Score:")
    print(best["Model"])
    print("F1 Score:", best["F1 Score"])