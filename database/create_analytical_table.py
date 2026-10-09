import psycopg2


# ==========================================
# POSTGRESQL CONNECTION DETAILS
# ==========================================

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "student_performance_db"
DB_USER = "postgres"
DB_PASSWORD = "1464"


# ==========================================
# CONNECT TO DATABASE
# ==========================================

try:

    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = connection.cursor()

    print("Connected to PostgreSQL successfully!")


    # ==========================================
    # DELETE OLD ANALYTICAL TABLE
    # ==========================================

    cursor.execute("""
        DROP TABLE IF EXISTS student_performance_analytics;
    """)

    connection.commit()


    # ==========================================
    # CREATE ANALYTICAL TABLE
    # ==========================================

    create_table_query = """

    CREATE TABLE student_performance_analytics AS

    SELECT

        ROW_NUMBER() OVER (
            ORDER BY "school", "sex", "age"
        ) AS student_id,

        "school",
        "sex",
        "age",
        "address",
        "famsize",
        "Pstatus",
        "Medu",
        "Fedu",
        "Mjob",
        "Fjob",
        "studytime",
        "failures",
        "schoolsup",
        "famsup",
        "paid",
        "activities",
        "higher",
        "internet",
        "romantic",
        "famrel",
        "freetime",
        "goout",
        "Dalc",
        "Walc",
        "health",
        "absences",
        "G1",
        "G2",
        "G3",


        -- Average internal marks
        ROUND(
            (
                CAST("G1" AS NUMERIC)
                + CAST("G2" AS NUMERIC)
            ) / 2.0,
            2
        ) AS average_internal_marks,


        -- Overall average marks
        ROUND(
            (
                CAST("G1" AS NUMERIC)
                + CAST("G2" AS NUMERIC)
                + CAST("G3" AS NUMERIC)
            ) / 3.0,
            2
        ) AS average_marks,


        -- Performance change
        (
            CAST("G3" AS NUMERIC)
            - CAST("G1" AS NUMERIC)
        ) AS performance_change,


        -- Final grade change
        (
            CAST("G3" AS NUMERIC)
            - CAST("G2" AS NUMERIC)
        ) AS final_grade_change,


        -- Previous failures
        "failures" AS previous_failures,


        -- Absence category
        CASE

            WHEN CAST("absences" AS NUMERIC) = 0
                THEN 'No Absence'

            WHEN CAST("absences" AS NUMERIC) <= 5
                THEN 'Low Absence'

            WHEN CAST("absences" AS NUMERIC) <= 15
                THEN 'Medium Absence'

            ELSE 'High Absence'

        END AS absence_category,


        -- Performance category
        CASE

            WHEN CAST("G3" AS NUMERIC) >= 16
                THEN 'Excellent'

            WHEN CAST("G3" AS NUMERIC) >= 12
                THEN 'Good'

            WHEN CAST("G3" AS NUMERIC) >= 10
                THEN 'Average'

            ELSE 'At Risk'

        END AS performance_category,


        -- Risk level
        CASE

            WHEN CAST("failures" AS NUMERIC) >= 2
                 OR CAST("G3" AS NUMERIC) < 10
                THEN 'High Risk'

            WHEN CAST("failures" AS NUMERIC) = 1
                 OR CAST("G3" AS NUMERIC) < 12
                THEN 'Medium Risk'

            ELSE 'Low Risk'

        END AS risk_level


    FROM student_cleaned;

    """


    cursor.execute(create_table_query)

    connection.commit()

    print("Analytical table created successfully!")


    # ==========================================
    # COUNT RECORDS
    # ==========================================

    cursor.execute("""
        SELECT COUNT(*)
        FROM student_performance_analytics;
    """)

    count = cursor.fetchone()[0]

    print("Total analytical records:", count)


    # ==========================================
    # SHOW SAMPLE DATA
    # ==========================================

    cursor.execute("""
        SELECT
            student_id,
            "G1",
            "G2",
            "G3",
            average_internal_marks,
            average_marks,
            performance_change,
            absence_category,
            performance_category,
            risk_level

        FROM student_performance_analytics

        LIMIT 10;
    """)


    rows = cursor.fetchall()

    print("\nSample analytical data:")

    for row in rows:
        print(row)


    # ==========================================
    # CLOSE CONNECTION
    # ==========================================

    cursor.close()

    connection.close()

    print("\n===================================")
    print("ANALYTICAL TABLE CREATION COMPLETE")
    print("===================================")


except Exception as e:

    print("\nERROR:")
    print(e)