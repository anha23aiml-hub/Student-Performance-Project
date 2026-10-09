import pandas as pd
import psycopg2


# =====================================================
# POSTGRESQL DETAILS
# =====================================================

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "student_performance_db"
DB_USER = "postgres"
DB_PASSWORD = "1464"


# =====================================================
# CSV FILE LOCATION
# =====================================================

CSV_FILE = "../data/cleaned/student_cleaned.csv"


# =====================================================
# CONNECT TO POSTGRESQL
# =====================================================

try:

    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    print("PostgreSQL connection successful!")

    cursor = connection.cursor()


    # =================================================
    # READ CLEANED CSV
    # =================================================

    print("Reading cleaned CSV...")

    df = pd.read_csv(CSV_FILE)

    print("CSV loaded successfully!")

    print("Number of rows:", len(df))
    print("Number of columns:", len(df.columns))

    print("\nColumns:")
    print(df.columns.tolist())


    # =================================================
    # CREATE TABLE
    # =================================================

    columns = []

    for column in df.columns:

        columns.append(
            '"' + column.replace('"', '""') + '" TEXT'
        )

    create_table_query = """
    CREATE TABLE IF NOT EXISTS student_cleaned (
        {}
    );
    """.format(", ".join(columns))


    cursor.execute(create_table_query)

    connection.commit()

    print("\nTable 'student_cleaned' created successfully!")


    # =================================================
    # INSERT DATA
    # =================================================

    print("Inserting data into PostgreSQL...")

    column_names = [
        '"' + column.replace('"', '""') + '"'
        for column in df.columns
    ]

    placeholders = ", ".join(
        ["%s"] * len(df.columns)
    )

    insert_query = """
    INSERT INTO student_cleaned ({})
    VALUES ({});
    """.format(
        ", ".join(column_names),
        placeholders
    )


    for row in df.itertuples(
        index=False,
        name=None
    ):

        cursor.execute(
            insert_query,
            row
        )


    connection.commit()


    print("Data inserted successfully!")

    print(
        "Total records inserted:",
        len(df)
    )


    # =================================================
    # CLOSE CONNECTION
    # =================================================

    cursor.close()
    connection.close()

    print("\n===================================")
    print("DATA LOADING COMPLETED")
    print("===================================")


except Exception as e:

    print("\nERROR:")
    print(e)