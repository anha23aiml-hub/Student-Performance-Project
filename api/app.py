import os

import mlflow
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Student Performance Risk Prediction API",
    description=(
        "Predict whether a student is at risk based on "
        "academic and personal factors."
    ),
    version="1.0.0",
)

# Load the model from the local exported folder.
MODEL_PATH = os.getenv("MODEL_PATH", "model_export")

model = mlflow.pyfunc.load_model(MODEL_PATH)


class StudentData(BaseModel):
    age: int
    sex: str
    address: str
    Medu: int
    Fedu: int
    studytime: int
    failures: int
    schoolsup: str
    famsup: str
    paid: str
    activities: str
    higher: str
    internet: str
    romantic: str
    famrel: int
    freetime: int
    goout: int
    Dalc: int
    Walc: int
    health: int
    absences: int
    G1: int
    G2: int


@app.get("/")
def home():
    return {
        "message": "Student Performance Risk Prediction API is running",
        "model": "StudentPerformanceRiskModel",
        "version": 2,
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
def predict(data: StudentData):
    try:
        student_df = pd.DataFrame([data.model_dump()])

        prediction = int(model.predict(student_df)[0])

        risk_status = (
            "At Risk" if prediction == 1 else "Not At Risk"
        )

        return {
            "prediction": prediction,
            "risk_status": risk_status,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(error)}",
        )
