import pandas as pd

df = pd.read_csv("student_cleaned.csv")

print("Number of rows:", len(df))

print("\nColumn names:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())