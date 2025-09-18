import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="Sleep Tracker", layout="centered")

# Replace with your published Google Sheet CSV link
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNjtRwQwXXtX7vVHh_na6Ky1y3dA7mMBpe5q6ycZXzSj8o_zKE1pcolI7YXOxTP1Msd2hYT9hScv0Q/pub?output=csv"

st.title("🛌 Sleep Tracker")

# Load sheet
try:
    df = pd.read_csv(SHEET_CSV_URL)
except Exception as e:
    st.error("Could not load Google Sheet. Check your link.")
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
        start = datetime.strptime(start_str, "%H:%M")
        end = datetime.strptime(end_str, "%H:%M")
        if end <= start:
            end += timedelta(days=1)
        return round((end - start).total_seconds() / 3600, 2)
    except Exception:
        return None

df["Duration (hrs)"] = df.apply(lambda row: calculate_sleep(row["Start"], row["End"]), axis=1)

# --- Show Table ---
st.subheader("Sleep Log")
st.dataframe(df, use_container_width=True)

# --- Stats ---
if df["Duration (hrs)"].notna().any():
    st.metric("Average Sleep", f"{df['Duration (hrs)'].mean():.2f} hrs")
    st.metric("Total Sleep", f"{df['Duration (hrs)'].sum():.2f} hrs")

    # --- Chart ---
    st.subheader("Sleep Chart")
    fig, ax = plt.subplots(figsize=(7,4))
    ax.bar(df["Date"].astype(str), df["Duration (hrs)"])
    ax.axhline(8, color="r", linestyle="--", label="Recommended 8 hrs")
    ax.set_ylabel("Hours Slept")
    ax.set_title("Sleep Duration")
    plt.xticks(rotation=30, ha="right")
    ax.legend()
    st.pyplot(fig)
else:
    st.info("No valid duration data found yet.")
