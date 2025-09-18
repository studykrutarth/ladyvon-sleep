import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Sleep Tracker", layout="centered")

# Replace with your Google Sheet published CSV link
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

        # If start == end → assume 0 hrs
        if start == end:
            return 0.0

        # Handle crossing midnight
        if end <= start:
            end += timedelta(days=1)

        hours = (end - start).total_seconds() / 3600.0

        # Cap at 16 hrs to avoid errors
        if hours > 16:
            return None
        return round(hours, 2)
    except Exception:
        return None

df["Duration (hrs)"] = df.apply(lambda row: calculate_sleep(row["Start"], row["End"]), axis=1)

# --- Show data ---

# --- Stats ---
if df["Duration (hrs)"].notna().any():
    st.metric("Average Sleep", f"{df['Duration (hrs)'].mean():.2f} hrs")
    st.metric("Total Sleep", f"{df['Duration (hrs)'].sum():.2f} hrs")

    # --- Charts (native) ---
    st.subheader("Sleep Duration (Bar Chart)")
    st.bar_chart(df.set_index("Date")["Duration (hrs)"])

    st.subheader("Sleep Trend (Line Chart)")
    st.line_chart(df.set_index("Date")["Duration (hrs)"])
else:
    st.info("No valid duration data found yet.")
st.subheader("Sleep Log")
st.dataframe(df, use_container_width=True)

