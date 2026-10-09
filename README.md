# 🎓 Student Performance Analytics

## 📌 Project Overview

Student Performance Analytics is a data analytics project that analyzes
student academic performance, attendance, previous failures, and risk levels.

The project uses Python for data processing, PostgreSQL for data storage
and analysis, and Streamlit for creating an interactive dashboard.

The main goal of this project is to identify students who may need
additional academic support based on their performance and attendance.

---

## 🎯 Objectives

The main objectives of this project are:

- Analyze student academic performance.
- Clean and prepare student data.
- Store cleaned data in PostgreSQL.
- Create an analytical database table.
- Calculate student performance metrics.
- Analyze attendance and academic performance.
- Identify high-risk students.
- Build an interactive dashboard.
- Provide useful insights and recommendations.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Data processing and analysis |
| Pandas | Data cleaning and manipulation |
| PostgreSQL | Database storage |
| SQL | Data analysis |
| Psycopg2 | PostgreSQL connection |
| SQLAlchemy | Database connection for dashboard |
| Streamlit | Interactive dashboard |
| Plotly | Data visualization |
| VS Code | Development environment |
| pgAdmin | PostgreSQL database management |

---

## 📂 Dataset

The project uses the Student Performance dataset.

Main dataset:

`student-mat.csv`

The dataset contains information about:

- School
- Gender
- Age
- Family information
- Study time
- Previous failures
- Support systems
- Internet access
- Alcohol consumption
- Absences
- G1
- G2
- G3

Where:

- G1 = First-period grade
- G2 = Second-period grade
- G3 = Final grade

---

# 🏗️ Project Architecture

The project follows this data processing workflow:

```text
Student Dataset
      ↓
Data Cleaning
      ↓
Cleaned CSV
      ↓
PostgreSQL Database
      ↓
Analytical Table
      ↓
SQL Analysis
      ↓
Streamlit Dashboard
      ↓
Insights and Recommendations