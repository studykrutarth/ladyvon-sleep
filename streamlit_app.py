# streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date, time

st.set_page_config(page_title="Sleep Tracker", layout="centered")

# Keep sleep data in session_state (resets if app restarts)
if "sleep_data" not in st.session_state:
    st.session_state.sleep_data = []

def calculate_sleep(start_time_str, end_time_str):
    start = datetime.strptime(start_time_str, "%H:%M")
    end = datetime.strptime(end_time_str, "%H:%M")
    if end <= start:
        end += timedelta(days=1)
    return round((end - start).total_seconds() / 3600, 2)

st.title("🛌 Sleep Tracker")

# Input form (you use this to add data)
with st.form("sleep_form"):
    d = st.date_input("Date", value=date.today())
    start_t = st.time_input("Sleep time", value=time(23, 0))
    end_t = st.time_input("Wake time", value=time(7, 0))
    submitted = st.form_submit_button("Add entry")
    if submitted:
        start_s = start_t.strftime("%H:%M")
        end_s = end_t.strftime("%H:%M")
        hrs = calculate_sleep(start_s, end_s)
        st.session_state.sleep_data.append(
            {"Date": d, "Start": start_s, "End": end_s, "Duration (hrs)": hrs}
        )
        st.success(f"Added: {hrs} hrs")

# Convert to DataFrame
df = pd.DataFrame(st.session_state.sleep_data)

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
