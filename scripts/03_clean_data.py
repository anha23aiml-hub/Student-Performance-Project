import pandas as pd

print("Cleaning started!")

# Read raw dataset
df = pd.read_csv("data/raw/student-mat.csv", sep=";")

print("Dataset loaded!")
print("Original rows:", len(df))

# Remove duplicate rows
df = df.drop_duplicates()

# Check missing values
print("\nMissing values:")
print(df.isnull().sum())

# Save cleaned dataset
df.to_csv(
    "data/cleaned/student_cleaned.csv",
    index=False
)

print("\nCleaning completed!")
print("Cleaned rows:", len(df))
print("File saved successfully!")