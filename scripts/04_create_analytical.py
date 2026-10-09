import pandas as pd

print("Program started!")

df = pd.read_csv("data/cleaned/student_cleaned.csv")

print("File loaded successfully!")
print("Rows:", len(df))
print("Columns:")
print(df.columns.tolist())