import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px


# ==========================================
# PAGE SETTINGS
# ==========================================

st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="🎓",
    layout="wide"
)


# ==========================================
# DATABASE DETAILS
# ==========================================

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "student_performance_db"
DB_USER = "postgres"
DB_PASSWORD = "1464"


# ==========================================
# DATABASE CONNECTION
# ==========================================

try:

    database_url = (
        f"postgresql+psycopg2://"
        f"{DB_USER}:{DB_PASSWORD}@"
        f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    engine = create_engine(database_url)

except Exception as e:

    st.error("Database connection could not be created.")
    st.write(e)
    st.stop()


# ==========================================
# LOAD DATA
# ==========================================

try:

    df = pd.read_sql(
        """
        SELECT *
        FROM student_performance_analytics;
        """,
        engine
    )

except Exception as e:

    st.error("Could not load data from PostgreSQL.")
    st.write(e)
    st.stop()


# ==========================================
# DATA TYPES
# ==========================================

for column in ["G1", "G2", "G3", "absences", "previous_failures"]:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ==========================================
# TITLE
# ==========================================

st.title("🎓 Student Performance Analytics")

st.write(
    "Analysis of student academic performance, "
    "attendance and risk levels."
)


# ==========================================
# SIDEBAR FILTERS
# ==========================================

st.sidebar.header("🔎 Student Filters")


school_filter = st.sidebar.multiselect(
    "Select School",
    options=sorted(df["school"].dropna().unique()),
    default=sorted(df["school"].dropna().unique())
)


gender_filter = st.sidebar.multiselect(
    "Select Gender",
    options=sorted(df["sex"].dropna().unique()),
    default=sorted(df["sex"].dropna().unique())
)


risk_filter = st.sidebar.multiselect(
    "Select Risk Level",
    options=sorted(df["risk_level"].dropna().unique()),
    default=sorted(df["risk_level"].dropna().unique())
)


performance_filter = st.sidebar.multiselect(
    "Select Performance",
    options=sorted(
        df["performance_category"]
        .dropna()
        .unique()
    ),
    default=sorted(
        df["performance_category"]
        .dropna()
        .unique()
    )
)


# ==========================================
# APPLY FILTERS
# ==========================================

filtered_df = df[
    (df["school"].isin(school_filter))
    &
    (df["sex"].isin(gender_filter))
    &
    (df["risk_level"].isin(risk_filter))
    &
    (
        df["performance_category"]
        .isin(performance_filter)
    )
].copy()


# ==========================================
# FILTERED OVERVIEW
# ==========================================

st.subheader("🔎 Filtered Student Overview")

st.write(
    f"Students matching selected filters: "
    f"**{len(filtered_df)}**"
)


if len(filtered_df) == 0:

    st.warning(
        "No students match the selected filters."
    )

    st.stop()


# ==========================================
# KPI SECTION
# ==========================================

col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Total Students",
    len(filtered_df)
)


col2.metric(
    "Average G3",
    round(filtered_df["G3"].mean(), 2)
)


col3.metric(
    "Average Absences",
    round(
        filtered_df["absences"].mean(),
        2
    )
)


high_risk_count = (
    filtered_df["risk_level"]
    .eq("High Risk")
    .sum()
)


col4.metric(
    "High Risk Students",
    int(high_risk_count)
)


st.divider()


# ==========================================
# ACADEMIC PERFORMANCE
# ==========================================

st.subheader(
    "📈 Average Academic Performance"
)


grade_data = pd.DataFrame({

    "Grade": [
        "G1",
        "G2",
        "G3"
    ],

    "Average Marks": [

        filtered_df["G1"].mean(),

        filtered_df["G2"].mean(),

        filtered_df["G3"].mean()

    ]

})


fig_grade = px.bar(

    grade_data,

    x="Grade",

    y="Average Marks",

    title="Average G1, G2 and G3",

    text_auto=".2f"

)


st.plotly_chart(
    fig_grade,
    width="stretch"
)


# ==========================================
# RISK DISTRIBUTION
# ==========================================

st.subheader(
    "⚠️ Student Risk Distribution"
)


risk_data = (

    filtered_df["risk_level"]

    .value_counts()

    .reset_index()

)


risk_data.columns = [

    "Risk Level",

    "Students"

]


fig_risk = px.pie(

    risk_data,

    names="Risk Level",

    values="Students",

    title="Risk Level Distribution"

)


st.plotly_chart(
    fig_risk,
    width="stretch"
)


# ==========================================
# PERFORMANCE DISTRIBUTION
# ==========================================

st.subheader(
    "🎓 Performance Distribution"
)


performance_data = (

    filtered_df[
        "performance_category"
    ]

    .value_counts()

    .reset_index()

)


performance_data.columns = [

    "Performance Category",

    "Students"

]


fig_performance = px.bar(

    performance_data,

    x="Performance Category",

    y="Students",

    title="Student Performance Categories",

    text_auto=True

)


st.plotly_chart(
    fig_performance,
    width="stretch"
)


# ==========================================
# SCHOOL PERFORMANCE
# ==========================================

st.subheader(
    "🏫 School-wise Performance"
)


school_data = (

    filtered_df

    .groupby("school")["G3"]

    .mean()

    .reset_index()

)


school_data.columns = [

    "School",

    "Average G3"

]


fig_school = px.bar(

    school_data,

    x="School",

    y="Average G3",

    title="Average Final Grade by School",

    text_auto=".2f"

)


st.plotly_chart(
    fig_school,
    width="stretch"
)


# ==========================================
# ABSENCE ANALYSIS
# ==========================================

st.subheader(
    "📅 Absence vs Final Performance"
)


absence_data = (

    filtered_df

    .groupby(
        "absence_category"
    )["G3"]

    .mean()

    .reset_index()

)


absence_data.columns = [

    "Absence Category",

    "Average G3"

]


fig_absence = px.bar(

    absence_data,

    x="Absence Category",

    y="Average G3",

    title="Average Final Grade by Absence Category",

    text_auto=".2f"

)


st.plotly_chart(
    fig_absence,
    width="stretch"
)


# ==========================================
# HIGH-RISK ANALYSIS
# ==========================================

st.divider()

st.header(
    "⚠️ High-Risk Student Analysis"
)


high_risk_df = filtered_df[
    filtered_df["risk_level"] == "High Risk"
].copy()


risk_col1, risk_col2, risk_col3 = st.columns(3)


risk_col1.metric(
    "High-Risk Students",
    len(high_risk_df)
)


if len(high_risk_df) > 0:

    risk_col2.metric(
        "High-Risk Average G3",
        round(
            high_risk_df["G3"].mean(),
            2
        )
    )


    risk_col3.metric(
        "High-Risk Average Absences",
        round(
            high_risk_df["absences"].mean(),
            2
        )
    )


# ==========================================
# HIGH-RISK TABLE
# ==========================================

if len(high_risk_df) > 0:

    st.subheader(
        "👨‍🎓 Students Requiring Attention"
    )


    high_risk_columns = [

        "student_id",

        "school",

        "sex",

        "age",

        "G1",

        "G2",

        "G3",

        "absences",

        "previous_failures",

        "performance_category",

        "risk_level"

    ]


    st.dataframe(

        high_risk_df[
            high_risk_columns
        ],

        width="stretch",

        hide_index=True

    )


# ==========================================
# INDIVIDUAL STUDENT ANALYSIS
# ==========================================

st.divider()

st.header(
    "🔍 Individual Student Analysis"
)


student_ids = sorted(
    df["student_id"].dropna().unique()
)


selected_student = st.selectbox(
    "Select Student ID",
    student_ids
)


student = df[
    df["student_id"] == selected_student
]


if len(student) > 0:

    student = student.iloc[0]


    st.subheader(
        f"Student ID: {selected_student}"
    )


    student_col1, student_col2, student_col3, student_col4 = st.columns(4)


    student_col1.metric(
        "G1",
        student["G1"]
    )


    student_col2.metric(
        "G2",
        student["G2"]
    )


    student_col3.metric(
        "G3",
        student["G3"]
    )


    student_col4.metric(
        "Absences",
        student["absences"]
    )


    st.write(
        "**School:**",
        student["school"]
    )


    st.write(
        "**Gender:**",
        student["sex"]
    )


    st.write(
        "**Age:**",
        student["age"]
    )


    st.write(
        "**Previous Failures:**",
        student["previous_failures"]
    )


    st.write(
        "**Performance Category:**",
        student["performance_category"]
    )


    st.write(
        "**Risk Level:**",
        student["risk_level"]
    )


    # Individual marks chart

    individual_marks = pd.DataFrame({

        "Exam": [
            "G1",
            "G2",
            "G3"
        ],

        "Marks": [

            student["G1"],

            student["G2"],

            student["G3"]

        ]

    })


    fig_student = px.bar(

        individual_marks,

        x="Exam",

        y="Marks",

        title="Individual Student Performance",

        text_auto=True

    )


    st.plotly_chart(

        fig_student,

        width="stretch"

    )


# ==========================================
# RECOMMENDATIONS
# ==========================================

st.divider()

st.header("💡 Recommendations")


st.write(
    "• Monitor students with high absence levels."
)

st.write(
    "• Pay attention to students with repeated failures."
)

st.write(
    "• Use G1 and G2 results to identify students "
    "who may need support before the final examination."
)

st.write(
    "• Encourage regular attendance and continuous "
    "academic monitoring."
)


# ==========================================
# ALL STUDENT DETAILS
# ==========================================

st.divider()

st.subheader(
    "👨‍🎓 All Filtered Student Details"
)


display_columns = [

    "student_id",

    "school",

    "sex",

    "age",

    "G1",

    "G2",

    "G3",

    "absences",

    "performance_category",

    "risk_level"

]


st.dataframe(

    filtered_df[
        display_columns
    ],

    width="stretch",

    hide_index=True

)


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.write(
    "🎓 Student Performance Analytics Project"
)