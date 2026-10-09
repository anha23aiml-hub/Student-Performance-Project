import pandas as pd
import os

# Load cleaned student data
input_file = "data/cleaned/student_cleaned.csv"
df = pd.read_csv(input_file)

print("Original rows:", len(df))

# Create target
# G3 < 10 = At Risk
# G3 >= 10 = Not At Risk
df["target"] = (df["G3"] < 10).astype(int)

# Select features
features = [
    "age",
    "sex",
    "address",
    "Medu",
    "Fedu",
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
    "G2"
]

# Create ML dataset
ml_df = df[features + ["target"]]

# Create output folder if it does not exist
os.makedirs("data/ml", exist_ok=True)

# Save ML dataset
output_file = "data/ml/student_ml.csv"
ml_df.to_csv(output_file, index=False)

print("ML dataset created successfully!")
print("Rows:", len(ml_df))
print("Columns:", len(ml_df.columns))
print("Saved to:", output_file)

print("\nTarget distribution:")
print(ml_df["target"].value_counts())