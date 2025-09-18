import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Sleep Tracker", layout="centered")

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNjtRwQwXXtX7vVHh_na6Ky1y3dA7mMBpe5q6ycZXzSj8o_zKE1pcolI7YXOxTP1Msd2hYT9hScv0Q/pub?output=csv"

st.title("🛌 Sleep Tracker")

# --- Load sheet ---
try:
    df = pd.read_csv(SHEET_CSV_URL)
except Exception as e:
    st.error("Could not load Google Sheet. Check your published CSV link.")
    st.stop()

# Ensure correct columns
expected_cols = ["Date", "Start", "End"]
for col in expected_cols:
    if col not in df.columns:
        st.error(f"Missing column: {col}. Your sheet must have {expected_cols}")
        st.stop()

# --- Calculate Duration ---
def calculate_sleep(start_str, end_str):
    try:
        start = datetime.strptime(start_str.strip(), "%H:%M")
        end = datetime.strptime(end_str.strip(), "%H:%M")

        if start == end:  # same time = 0 hrs
            return 0.0
        if end <= start:  # crossed midnight
            end += timedelta(days=1)

        hours = (end - start).total_seconds() / 3600.0
        if hours > 16:  # unrealistic, discard
            return None
        return round(hours, 2)
    except Exception:
        return None

df["Duration (hrs)"] = df.apply(lambda row: calculate_sleep(row["Start"], row["End"]), axis=1)



# --- Stats ---
if df["Duration (hrs)"].notna().any():
    st.metric("Average Sleep", f"{df['Duration (hrs)'].mean():.2f} hrs")
    st.metric("Total Sleep", f"{df['Duration (hrs)'].sum():.2f} hrs")

    # --- Plotly Bar Chart ---
    st.subheader("Sleep Duration (Bar Chart)")
    fig_bar = px.bar(
        df,
        x="Date",
        y="Duration (hrs)",
        text="Duration (hrs)",
        title="Sleep Duration per Day",
        labels={"Duration (hrs)": "Hours Slept"},
    )
    fig_bar.add_hline(
        y=8, line_dash="dash", line_color="red", annotation_text="Recommended 8 hrs"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Plotly Line Chart ---
    st.subheader("Sleep Trend (Line Chart)")
    fig_line = px.line(
        df,
        x="Date",
        y="Duration (hrs)",
        markers=True,
        title="Sleep Trend Over Time",
        labels={"Duration (hrs)": "Hours Slept"},
    )
    fig_line.add_hline(
        y=8, line_dash="dash", line_color="red", annotation_text="Recommended 8 hrs"
    )
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("No valid duration data found yet.")

# --- Show data ---
st.subheader("Sleep Log")
st.dataframe(df, use_container_width=True)
