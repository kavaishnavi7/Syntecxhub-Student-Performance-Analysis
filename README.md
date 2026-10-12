# SyntecxHub Student Performance Analysis

An interactive data-analysis project for exploring Mathematics, Reading, and Writing scores, comparing available student groups, and reviewing possible areas for academic support. It includes a Streamlit dashboard, a reproducible analysis script, a Jupyter notebook, and generated output tables and charts.

## Live dashboard

Explore the deployed app on [Streamlit Community Cloud](https://syntecxapp-student-performance-analysis-jajwteyddcvv6dqyufcmel.streamlit.app/).

## Features

- Validates required dataset columns, converts score fields to numeric values, removes exact duplicate rows, and bounds scores to 0–100.
- Calculates overall averages and illustrative performance bands.
- Compares subject averages and score distributions across dataset groups.
- Provides interactive group filters, Plotly visualizations, a student-level explorer, and filtered CSV downloads.
- Reports missing values and describes important data limitations.

## Dataset

The `data/` folder contains CSV and Excel versions of the supplied 100-row dataset. The expected columns are `Student ID`, `Gender`, `Ethnicity`, `Parental Education`, `Test Preparation`, `Math Score`, `Reading Score`, and `Writing Score`.

The records use coded student IDs, but include student-level scores and demographic categories. Before making this repository public, confirm that the data is synthetic or that public sharing is authorized. Do not publish actual student records or other sensitive data.

The dataset does not contain attendance, study hours, class/section, or assessment dates. `Test Preparation` is missing in many records; missing values are treated as unknown, not as “Not completed.” Group comparisons are descriptive and do not establish causation. Performance bands are illustrative rather than official grading standards.

## Tools

- Python 3.10+
- Pandas and Matplotlib
- Streamlit and Plotly
- OpenPyXL for Excel file support
- Jupyter Notebook (optional, for working with the notebook)

## Run locally

From the project root, create and activate a virtual environment, then install the project dependencies:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Launch the interactive dashboard:

```bash
streamlit run app.py
```

The dashboard reads its default CSV from `data/student_performance_100.csv`. It also accepts CSV and Excel uploads.

To regenerate the static analysis tables and charts:

```bash
python analysis.py
```

To open and run the notebook, install Jupyter in the active environment if it is not already available:

```bash
python -m pip install jupyter
jupyter notebook notebooks/Student_Performance_Analysis.ipynb
```

## Streamlit Community Cloud

1. Push this project to a GitHub repository after confirming that all included data is safe and authorized for public access.
2. In Streamlit Community Cloud, select **Create app**, choose the repository and `main` branch, and set the main file path to `app.py`.
3. Deploy. The app uses repository-relative paths, so its default dataset is loaded from the committed `data/` folder.

No secrets or external service credentials are required by the current dashboard.
