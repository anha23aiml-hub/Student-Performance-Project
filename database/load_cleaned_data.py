import pandas as pd
import psycopg2

# ==========================================
# DATABASE DETAILS
# ==========================================

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "student_performance_db"
DB_USER = "postgres"
DB_PASSWORD = "1464"


# ==========================================
# READ CLEANED CSV
# ==========================================

csv_path = "../data/cleaned/student_cleaned.csv"

df = pd.read_csv(csv_path)

print("CSV loaded successfully!")
print("CSV rows:", len(df))


# ==========================================
# CONNECT TO POSTGRESQL
# ==========================================

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
# CLEAR OLD DATA
# ==========================================

cursor.execute("""
    DELETE FROM student_cleaned;
""")

connection.commit()

print("Old student_cleaned data deleted!")


# ==========================================
# INSERT CLEANED DATA
# ==========================================

columns = list(df.columns)

column_names = ", ".join(f'"{col}"' for col in columns)

placeholders = ", ".join(["%s"] * len(columns))

insert_query = f"""
    INSERT INTO student_cleaned ({column_names})
    VALUES ({placeholders});
"""

for _, row in df.iterrows():

    values = []

    for value in row:
        if pd.isna(value):
            values.append(None)
        else:
            values.append(value)

    cursor.execute(insert_query, values)


connection.commit()

print("Cleaned data inserted successfully!")


# ==========================================
# CHECK ROW COUNT
# ==========================================

cursor.execute("""
    SELECT COUNT(*)
    FROM student_cleaned;
""")

count = cursor.fetchone()[0]

print("Total student_cleaned records:", count)


# ==========================================
# CLOSE CONNECTION
# ==========================================

cursor.close()
connection.close()

print("\n===================================")
print("CLEANED DATA LOADING COMPLETE")
print("===================================")