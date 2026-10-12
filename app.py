import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Student Performance Analytics", page_icon="🎓", layout="wide")

ROOT = Path(__file__).parent
DEFAULT_DATA = ROOT / "data" / "student_performance_100.csv"

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file) if uploaded_file.name.lower().endswith(".csv") else pd.read_excel(uploaded_file)
    else:
        data = pd.read_csv(DEFAULT_DATA)
    score_cols = ["Math Score", "Reading Score", "Writing Score"]
    required = ["Student ID", "Gender", "Ethnicity", "Parental Education", *score_cols]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    for col in score_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    data = data.drop_duplicates().copy()
    data[score_cols] = data[score_cols].clip(0, 100)
    data["Overall Average"] = data[score_cols].mean(axis=1)
    data["Performance Band"] = pd.cut(
        data["Overall Average"],
        bins=[-0.01, 39.99, 59.99, 79.99, 100],
        labels=["Needs support", "Developing", "Proficient", "Advanced"]
    )
    return data

st.title("🎓 Student Performance Analysis")
st.caption("Explore subject scores, student groups, test preparation, and potential areas for academic support.")
uploaded = st.sidebar.file_uploader("Upload a CSV or Excel dataset", type=["csv", "xlsx", "xls"])
try:
    data = load_data(uploaded)
except Exception as exc:
    st.error(f"Could not load dataset: {exc}")
    st.stop()

score_cols = ["Math Score", "Reading Score", "Writing Score"]
st.sidebar.header("Filters")
group_col = st.sidebar.selectbox("Group students by", ["Gender", "Ethnicity", "Parental Education"] + (["Test Preparation"] if "Test Preparation" in data.columns else []))
group_values = sorted(data[group_col].dropna().astype(str).unique().tolist())
selected = st.sidebar.multiselect("Select group values", group_values, default=group_values)
filtered = data[data[group_col].astype(str).isin(selected)].copy() if selected else data.iloc[0:0].copy()

n = len(filtered)
overall = filtered["Overall Average"].mean() if n else 0
pass_rate = (filtered["Overall Average"] >= 50).mean() * 100 if n else 0
best_subject = filtered[score_cols].mean().idxmax() if n else "—"
c1, c2, c3, c4 = st.columns(4)
c1.metric("Students", f"{n:,}")
c2.metric("Mean overall score", f"{overall:.1f}/100" if n else "—")
c3.metric("At/above 50 average", f"{pass_rate:.1f}%" if n else "—")
c4.metric("Highest average subject", best_subject.replace(" Score", "") if n else "—")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Group comparisons", "Student explorer", "Data quality & notes"])
with tab1:
    left, right = st.columns(2)
    with left:
        subject_means = filtered[score_cols].mean().rename_axis("Subject").reset_index(name="Average score")
        subject_means["Subject"] = subject_means["Subject"].str.replace(" Score", "", regex=False)
        st.plotly_chart(px.bar(subject_means, x="Subject", y="Average score", color="Subject",
                               title="Average score by subject", range_y=[0, 100]), use_container_width=True)
        st.plotly_chart(px.line(subject_means, x="Subject", y="Average score", markers=True,
                                title="Subject average comparison (not a time trend)", range_y=[0, 100]),
                        use_container_width=True)
    with right:
        bands = filtered["Performance Band"].value_counts().reindex(
            ["Needs support", "Developing", "Proficient", "Advanced"], fill_value=0
        ).rename_axis("Performance band").reset_index(name="Students")
        st.plotly_chart(px.pie(bands, names="Performance band", values="Students",
                               title="Overall performance distribution", hole=0.35), use_container_width=True)
    st.plotly_chart(px.histogram(filtered, x="Overall Average", nbins=12,
                                 title="Distribution of overall average scores",
                                 labels={"Overall Average": "Overall average"}), use_container_width=True)
with tab2:
    grouped = filtered.groupby(group_col, dropna=False)[score_cols + ["Overall Average"]].mean().reset_index()
    melted = grouped.melt(id_vars=group_col, var_name="Subject", value_name="Average score")
    melted["Subject"] = melted["Subject"].str.replace(" Score", "", regex=False).str.replace("Overall Average", "Overall", regex=False)
    st.plotly_chart(px.bar(melted, x=group_col, y="Average score", color="Subject", barmode="group",
                           title=f"Average scores by {group_col}", range_y=[0, 100]), use_container_width=True)
    counts = filtered[group_col].value_counts(dropna=False).rename_axis(group_col).reset_index(name="Students")
    st.plotly_chart(px.bar(counts, x=group_col, y="Students", title=f"Student count by {group_col}"), use_container_width=True)
    if group_col == "Test Preparation":
        st.info("Interpret test-preparation comparisons carefully: this dataset has missing preparation status for many students.")
with tab3:
    st.dataframe(filtered[["Student ID", group_col, *score_cols, "Overall Average", "Performance Band"]].sort_values("Overall Average"),
                 use_container_width=True, hide_index=True)
    st.download_button("Download filtered data as CSV", filtered.to_csv(index=False).encode("utf-8"),
                       file_name="filtered_student_performance.csv", mime="text/csv")
with tab4:
    st.subheader("Dataset quality")
    missing = data.isna().sum().rename("Missing values").reset_index().rename(columns={"index": "Column"})
    st.dataframe(missing, use_container_width=True, hide_index=True)
    st.write(f"Exact duplicate rows: **{pd.read_excel(ROOT / 'data' / 'student_performance_100.xlsx').duplicated().sum()}**")
    st.subheader("Important limitations")
    st.markdown("""
    - The supplied dataset contains 100 students and marks for Math, Reading, and Writing.
    - It does **not** contain attendance, study hours, class/section, or time-series fields. Those requested analyses cannot be reliably performed from this file.
    - The `Test Preparation` column is missing for many records. Missing status is not automatically treated as “Not completed.”
    - Group differences are descriptive associations, not evidence that a demographic characteristic causes performance differences.
    - Performance bands are illustrative dashboard categories: below 40, 40–59.99, 60–79.99, and 80–100.
    """)
st.divider()
st.caption("Built for the SyntecxHub Student Performance Analysis project • Python, Pandas, Streamlit, Plotly")
