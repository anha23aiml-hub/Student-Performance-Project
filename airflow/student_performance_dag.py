
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import os

# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

# This path will be available inside Docker after mounting
BASE_DIR = "/opt/airflow/project"

RAW_FILE = os.path.join(
    BASE_DIR, "data", "raw", "student-mat.csv"
)

STAGING_FILE = os.path.join(
    BASE_DIR, "data", "staging", "student_staging.csv"
)

CLEANED_FILE = os.path.join(
    BASE_DIR, "data", "cleaned", "student_cleaned.csv"
)

ERROR_FILE = os.path.join(
    BASE_DIR, "logs", "rejected_records.csv"
)

ANALYTICAL_FILE = os.path.join(
    BASE_DIR, "data", "analytical", "student_analytical.csv"
)


# ---------------------------------------------------------
# CREATE REQUIRED FOLDERS
# ---------------------------------------------------------

def create_folders():
    folders = [
        os.path.dirname(STAGING_FILE),
        os.path.dirname(CLEANED_FILE),
        os.path.dirname(ERROR_FILE),
        os.path.dirname(ANALYTICAL_FILE),
    ]

    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    print("Required folders created.")


# ---------------------------------------------------------
# STEP 1: INGEST DATA
# ---------------------------------------------------------

def ingest_data():
    print("Starting data ingestion...")

    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_FILE}"
        )

    # UCI Student Performance CSV uses semicolons
    df = pd.read_csv(RAW_FILE, sep=";")

    os.makedirs(os.path.dirname(STAGING_FILE), exist_ok=True)
    df.to_csv(STAGING_FILE, index=False)

    print("Data ingestion completed.")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Staging file saved:", STAGING_FILE)


# ---------------------------------------------------------
# STEP 2: CLEAN DATA
# ---------------------------------------------------------

def clean_data():
    print("Starting data cleaning...")

    if not os.path.exists(STAGING_FILE):
        raise FileNotFoundError(
            f"Staging dataset not found: {STAGING_FILE}"
        )

    df = pd.read_csv(STAGING_FILE)
    original_rows = len(df)

    # Remove duplicate records
    df = df.drop_duplicates().copy()

    # Separate records containing missing values
    rejected = df[df.isnull().any(axis=1)].copy()
    df = df.dropna().copy()

    # Save rejected records
    os.makedirs(os.path.dirname(ERROR_FILE), exist_ok=True)
    rejected.to_csv(ERROR_FILE, index=False)

    # Save cleaned records
    os.makedirs(os.path.dirname(CLEANED_FILE), exist_ok=True)
    df.to_csv(CLEANED_FILE, index=False)

    print("Data cleaning completed.")
    print("Original rows:", original_rows)
    print("Cleaned rows:", len(df))
    print("Rejected rows:", len(rejected))
    print("Cleaned file saved:", CLEANED_FILE)


# ---------------------------------------------------------
# STEP 3: CREATE ANALYTICAL OUTPUT
# ---------------------------------------------------------

def create_analytical_data():
    print("Starting analytical data preparation...")

    if not os.path.exists(CLEANED_FILE):
        raise FileNotFoundError(
            f"Cleaned dataset not found: {CLEANED_FILE}"
        )

    df = pd.read_csv(CLEANED_FILE)

    # Calculate average of first and second period grades
    if "G1" in df.columns and "G2" in df.columns:
        df["average_score"] = (df["G1"] + df["G2"]) / 2

    # Categorize performance using final grade
    if "G3" in df.columns:
        df["performance_category"] = df["G3"].apply(
            lambda score: (
                "At Risk" if score < 10
                else "Good" if score < 15
                else "Excellent"
            )
        )

    os.makedirs(os.path.dirname(ANALYTICAL_FILE), exist_ok=True)
    df.to_csv(ANALYTICAL_FILE, index=False)

    print("Analytical data preparation completed.")
    print("Analytical records:", len(df))
    print("Analytical file saved:", ANALYTICAL_FILE)


# ---------------------------------------------------------
# AIRFLOW DAG CONFIGURATION
# ---------------------------------------------------------

default_args = {
    "owner": "student_performance_project",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="student_performance_pipeline",
    default_args=default_args,
    description="Student Performance Data Pipeline",
    schedule=None,
    catchup=False,
    tags=["student-performance", "data-pipeline"],
) as dag:

    create_folders_task = PythonOperator(
        task_id="create_folders",
        python_callable=create_folders,
    )

    ingestion_task = PythonOperator(
        task_id="ingest_data",
        python_callable=ingest_data,
    )

    cleaning_task = PythonOperator(
        task_id="clean_data",
        python_callable=clean_data,
    )

    analytical_task = PythonOperator(
        task_id="create_analytical_data",
        python_callable=create_analytical_data,
    )

    # Execute tasks in order
    create_folders_task >> ingestion_task
    ingestion_task >> cleaning_task
    cleaning_task >> analytical_task
