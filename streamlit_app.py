import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sleep Tracker", layout="centered")

# Replace with your published Google Sheet CSV link
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNjtRwQwXXtX7vVHh_na6Ky1y3dA7mMBpe5q6ycZXzSj8o_zKE1pcolI7YXOxTP1Msd2hYT9hScv0Q/pub?output=csv"

st.title("🛌 Sleep Tracker")

# Load data
try:
    df = pd.read_csv(SHEET_CSV_URL)
    # Make sure Duration is numeric
    if "Duration (hrs)" in df.columns:
        df["Duration (hrs)"] = pd.to_numeric(df["Duration (hrs)"], errors="coerce")
except Exception as e:
    st.error("Could not load Google Sheet. Check your link.")
    st.stop()


if not df.empty:
    st.subheader("Sleep Log")
    st.dataframe(df, use_container_width=True)

    st.metric("Average Sleep", f"{df['Duration (hrs)'].mean():.2f} hrs")
    st.metric("Total Sleep", f"{df['Duration (hrs)'].sum():.2f} hrs")

    st.subheader("Sleep Chart")
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(df["Date"].astype(str), df["Duration (hrs)"])
    ax.axhline(8, color="r", linestyle="--", label="Recommended 8 hrs")
    ax.set_ylabel("Hours Slept")
    ax.set_title("Sleep Duration")
    plt.xticks(rotation=30, ha="right")
    ax.legend()
    st.pyplot(fig)
else:
    st.info("No entries yet. Add some in your Google Sheet.")


