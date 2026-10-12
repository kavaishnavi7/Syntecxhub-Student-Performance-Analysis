"""Reproducible analysis for the SyntecxHub Student Performance Analysis project."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "student_performance_100.csv"
OUT = ROOT / "outputs"
CHARTS = OUT / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)
score_cols = ["Math Score", "Reading Score", "Writing Score"]
for col in score_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")
df = df.drop_duplicates().copy()
df[score_cols] = df[score_cols].clip(0, 100)
df["Overall Average"] = df[score_cols].mean(axis=1)
df["Performance Band"] = pd.cut(
    df["Overall Average"], [-0.01, 39.99, 59.99, 79.99, 100],
    labels=["Needs support", "Developing", "Proficient", "Advanced"]
)

OUT.mkdir(exist_ok=True)
df.to_csv(OUT / "cleaned_student_performance.csv", index=False)
df[score_cols + ["Overall Average"]].describe().round(2).to_csv(OUT / "score_summary.csv")
df.groupby("Gender")[score_cols + ["Overall Average"]].mean().round(2).to_csv(OUT / "gender_comparison.csv")
df.groupby("Ethnicity")[score_cols + ["Overall Average"]].mean().round(2).to_csv(OUT / "ethnicity_comparison.csv")
df.groupby("Parental Education")[score_cols + ["Overall Average"]].mean().round(2).to_csv(OUT / "parental_education_comparison.csv")
df["Performance Band"].value_counts().rename_axis("Performance Band").to_csv(OUT / "performance_band_counts.csv")

# 1. Subject average bar chart
means = df[score_cols].mean()
fig, ax = plt.subplots(figsize=(8, 5))
means.index = [x.replace(" Score", "") for x in means.index]
means.plot(kind="bar", ax=ax)
ax.set_title("Average Score by Subject")
ax.set_ylabel("Average score (0–100)")
ax.set_ylim(0, 100)
ax.grid(axis="y", alpha=0.25)
plt.tight_layout()
fig.savefig(CHARTS / "subject_average.png", dpi=160)
plt.close(fig)

# 1b. Line chart comparing mean scores across subjects (not a time trend)
fig, ax = plt.subplots(figsize=(8, 5))
line_means = df[score_cols].mean()
line_means.index = [x.replace(" Score", "") for x in line_means.index]
ax.plot(line_means.index, line_means.values, marker="o", linewidth=2)
ax.set_title("Subject Average Comparison")
ax.set_ylabel("Average score (0–100)")
ax.set_ylim(0, 100)
ax.grid(axis="y", alpha=0.25)
plt.tight_layout()
fig.savefig(CHARTS / "subject_average_line.png", dpi=160)
plt.close(fig)

# 2. Performance-band pie chart
fig, ax = plt.subplots(figsize=(7, 6))
df["Performance Band"].value_counts().reindex(
    ["Needs support", "Developing", "Proficient", "Advanced"], fill_value=0
).plot(kind="pie", autopct="%1.1f%%", ax=ax, ylabel="")
ax.set_title("Overall Performance Distribution")
plt.tight_layout()
fig.savefig(CHARTS / "performance_distribution.png", dpi=160)
plt.close(fig)

# 3. Group comparison chart
group_means = df.groupby("Gender")[score_cols].mean()
fig, ax = plt.subplots(figsize=(8, 5))
group_means.rename(columns={c: c.replace(" Score", "") for c in score_cols}).plot(kind="bar", ax=ax)
ax.set_title("Average Scores by Gender")
ax.set_ylabel("Average score (0–100)")
ax.set_ylim(0, 100)
ax.grid(axis="y", alpha=0.25)
plt.tight_layout()
fig.savefig(CHARTS / "gender_comparison.png", dpi=160)
plt.close(fig)

# 4. Correlation heatmap (scores only)
fig, ax = plt.subplots(figsize=(6, 5))
corr = df[score_cols + ["Overall Average"]].corr()
im = ax.imshow(corr, vmin=-1, vmax=1)
ax.set_xticks(range(len(corr.columns)), [c.replace(" Score", "") for c in corr.columns], rotation=35, ha="right")
ax.set_yticks(range(len(corr.index)), [c.replace(" Score", "") for c in corr.index])
for i in range(len(corr.index)):
    for j in range(len(corr.columns)):
        ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")
fig.colorbar(im, ax=ax, label="Correlation")
ax.set_title("Correlation Between Scores")
plt.tight_layout()
fig.savefig(CHARTS / "score_correlation.png", dpi=160)
plt.close(fig)

missing = pd.read_csv(DATA_PATH).isna().sum().rename("Missing values")
missing.to_csv(OUT / "missing_values.csv")

print(f"Students analyzed: {len(df)}")
print("\nAverage score by subject:")
print(df[score_cols].mean().round(2).to_string())
print(f"\nMean overall score: {df['Overall Average'].mean():.2f}")
print(f"Students with overall average >= 50: {(df['Overall Average'] >= 50).sum()} ({(df['Overall Average'] >= 50).mean()*100:.1f}%)")
print("\nMissing values:")
print(missing[missing > 0].to_string() if (missing > 0).any() else "None")
print(f"\nCharts and tables saved in: {OUT}")
