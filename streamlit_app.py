import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date, time
import os

st.set_page_config(page_title="Sleep Tracker", layout="centered")

CSV_FILE = "sleep_data.csv"

# --- Helper functions ---
def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, parse_dates=["Date"])
    return pd.DataFrame(columns=["Date", "Start", "End", "Duration (hrs)"])

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def calculate_sleep(start_time_str, end_time_str):
    start = datetime.strptime(start_time_str, "%H:%M")
    end = datetime.strptime(end_time_str, "%H:%M")
    if end <= start:
        end += timedelta(days=1)
    return round((end - start).total_seconds() / 3600, 2)

# --- Load existing data ---
df = load_data()

# --- UI ---
st.title("🛌 Sleep Tracker")

with st.form("sleep_form"):
    d = st.date_input("Date", value=date.today())
    start_t = st.time_input("Sleep time", value=time(23, 0))
    end_t = st.time_input("Wake time", value=time(7, 0))
    submitted = st.form_submit_button("Add entry")
    if submitted:
        start_s = start_t.strftime("%H:%M")
        end_s = end_t.strftime("%H:%M")
        hrs = calculate_sleep(start_s, end_s)
        new_entry = pd.DataFrame([{
            "Date": d,
            "Start": start_s,
            "End": end_s,
            "Duration (hrs)": hrs
        }])
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)
        st.success(f"Added: {hrs} hrs")

if not df.empty:
    st.subheader("Sleep Log")
    st.dataframe(df, use_container_width=True)

    # Summary
    st.metric("Average Sleep", f"{df['Duration (hrs)'].mean():.2f} hrs")
    st.metric("Total Sleep", f"{df['Duration (hrs)'].sum():.2f} hrs")

    # Plot
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
    st.info("No entries yet. Add your first sleep record above.")
