from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

import pandas as pd
import os


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

BASE_DIR = "C:\Users\Ananya\OneDrive\Documents\Student_Performance_Project>"

RAW_FILE = os.path.join(
    BASE_DIR,
    "data",
    "raw",
    "student_performance.csv"
)

STAGING_FILE = os.path.join(
    BASE_DIR,
    "data",
    "staging",
    "student_staging.csv"
)

CLEANED_FILE = os.path.join(
    BASE_DIR,
    "data",
    "cleaned",
    "student_cleaned.csv"
)

ERROR_FILE = os.path.join(
    BASE_DIR,
    "logs",
    "rejected_records.csv"
)


# ---------------------------------------------------------
# CREATE REQUIRED FOLDERS
# ---------------------------------------------------------

def create_folders():

    folders = [
        os.path.dirname(STAGING_FILE),
        os.path.dirname(CLEANED_FILE),
        os.path.dirname(ERROR_FILE)
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

    df = pd.read_csv(RAW_FILE)

    print("Dataset successfully read.")
    print("Number of rows:", len(df))
    print("Number of columns:", len(df.columns))

    # Add extraction date
    df["extraction_date"] = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    # Save staging data
    df.to_csv(STAGING_FILE, index=False)

    print("Staging file created:", STAGING_FILE)


# ---------------------------------------------------------
# STEP 2: VALIDATE AND CLEAN DATA
# ---------------------------------------------------------

def validate_and_clean():

    print("Starting validation and cleaning...")

    if not os.path.exists(STAGING_FILE):
        raise FileNotFoundError(
            "Staging file not found."
        )

    df = pd.read_csv(STAGING_FILE)

    print("Original rows:", len(df))

    # -----------------------------------------------------
    # Remove completely empty rows
    # -----------------------------------------------------

    df = df.dropna(how="all")

    # -----------------------------------------------------
    # Remove duplicate rows
    # -----------------------------------------------------

    duplicate_count = df.duplicated().sum()

    print("Duplicate rows:", duplicate_count)

    df = df.drop_duplicates()

    # -----------------------------------------------------
    # Find missing values
    # -----------------------------------------------------

    print("\nMissing values before cleaning:")

    print(df.isnull().sum())

    # -----------------------------------------------------
    # Handle numerical missing values
    # -----------------------------------------------------

    numeric_columns = df.select_dtypes(
        include=["int64", "float64"]
    ).columns

    for column in numeric_columns:

        if df[column].isnull().sum() > 0:

            df[column] = df[column].fillna(
                df[column].median()
            )

    # -----------------------------------------------------
    # Handle text missing values
    # -----------------------------------------------------

    text_columns = df.select_dtypes(
        include=["object"]
    ).columns

    for column in text_columns:

        if df[column].isnull().sum() > 0:

            df[column] = df[column].fillna(
                "Unknown"
            )

    # -----------------------------------------------------
    # Check for invalid marks
    #
    # UCI Student Performance uses G1, G2 and G3
    # as grades on a 0-20 scale.
    # -----------------------------------------------------

    mark_columns = [
        column
        for column in ["G1", "G2", "G3"]
        if column in df.columns
    ]

    rejected_records = []

    for column in mark_columns:

        invalid_rows = df[
            (df[column] < 0) |
            (df[column] > 20)
        ]

        if len(invalid_rows) > 0:

            rejected_records.append(
                invalid_rows
            )

            print(
                f"Invalid records found in {column}: "
                f"{len(invalid_rows)}"
            )

            df = df[
                (df[column] >= 0) &
                (df[column] <= 20)
            ]

    # -----------------------------------------------------
    # Save rejected records
    # -----------------------------------------------------

    if rejected_records:

        rejected_df = pd.concat(
            rejected_records,
            ignore_index=True
        )

        rejected_df.to_csv(
            ERROR_FILE,
            index=False
        )

        print(
            "Rejected records saved to:",
            ERROR_FILE
        )

    else:

        # Create an empty error file
        pd.DataFrame().to_csv(
            ERROR_FILE,
            index=False
        )

        print("No invalid records found.")

    # -----------------------------------------------------
    # Save cleaned data
    # -----------------------------------------------------

    df.to_csv(
        CLEANED_FILE,
        index=False
    )

    print(
        "Cleaned data saved to:",
        CLEANED_FILE
    )

    print(
        "Final number of rows:",
        len(df)
    )


# ---------------------------------------------------------
# STEP 3: CREATE ANALYTICAL DATA
# ---------------------------------------------------------

def create_analytical_data():

    print("Creating analytical dataset...")

    if not os.path.exists(CLEANED_FILE):
        raise FileNotFoundError(
            "Cleaned dataset not found."
        )

    df = pd.read_csv(CLEANED_FILE)

    # -----------------------------------------------------
    # Create average marks
    # -----------------------------------------------------

    mark_columns = [
        column
        for column in ["G1", "G2", "G3"]
        if column in df.columns
    ]

    if mark_columns:

        df["average_marks"] = df[
            mark_columns
        ].mean(axis=1)

    # -----------------------------------------------------
    # Create performance category
    # -----------------------------------------------------

    if "average_marks" in df.columns:

        df["performance_category"] = pd.cut(
            df["average_marks"],
            bins=[
                -1,
                9.99,
                13.99,
                16.99,
                20
            ],
            labels=[
                "Poor",
                "Average",
                "Good",
                "Excellent"
            ]
        )

    # -----------------------------------------------------
    # Create analytical folder
    # -----------------------------------------------------

    analytical_folder = os.path.join(
        BASE_DIR,
        "data",
        "analytical"
    )

    os.makedirs(
        analytical_folder,
        exist_ok=True
    )

    analytical_file = os.path.join(
        analytical_folder,
        "student_performance_analytical.csv"
    )

    # -----------------------------------------------------
    # Save analytical data
    # -----------------------------------------------------

    df.to_csv(
        analytical_file,
        index=False
    )

    print(
        "Analytical dataset created:",
        analytical_file
    )

    print(
        "Analytical rows:",
        len(df)
    )


# ---------------------------------------------------------
# AIRFLOW SETTINGS
# ---------------------------------------------------------

default_args = {

    "owner": "student",

    "depends_on_past": False,

    "retries": 1,

    "retry_delay": timedelta(minutes=2)

}


# ---------------------------------------------------------
# CREATE DAG
# ---------------------------------------------------------

with DAG(

    dag_id="student_performance_pipeline",

    default_args=default_args,

    description=(
        "Student Performance Data Engineering Pipeline"
    ),

    start_date=datetime(2026, 8, 26),

    schedule=None,

    catchup=False,

    tags=[
        "student",
        "data-engineering",
        "etl"
    ]

) as dag:


    # Task 1
    create_folders_task = PythonOperator(

        task_id="create_folders",

        python_callable=create_folders

    )


    # Task 2
    ingestion_task = PythonOperator(

        task_id="ingest_student_data",

        python_callable=ingest_data

    )


    # Task 3
    cleaning_task = PythonOperator(

        task_id="validate_and_clean_data",

        python_callable=validate_and_clean

    )


    # Task 4
    analytical_task = PythonOperator(

        task_id="create_analytical_data",

        python_callable=create_analytical_data

    )


    # -----------------------------------------------------
    # TASK ORDER
    # -----------------------------------------------------

    create_folders_task >> ingestion_task
    ingestion_task >> cleaning_task
    cleaning_task >> analytical_task