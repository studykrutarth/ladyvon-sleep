import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Sleep Tracker", layout="centered")

SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQNjtRwQwXXtX7vVHh_na6Ky1y3dA7mMBpe5q6ycZXzSj8o_zKE1pcolI7YXOxTP1Msd2hYT9hScv0Q/pub?output=csv"

st.title("Ladyvon Sleep Assumptions")

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

# If user added a Quality column (Good/Bad), use it; otherwise create Unknown
quality_col_candidates = ["Quality", "Sleep Quality", "Quality (Good/Bad)"]
quality_col = None
for c in quality_col_candidates:
    if c in df.columns:
        quality_col = c
        break

if quality_col is None:
    # create a default column so plotting code is simple
    df["Quality"] = "Unknown"
else:
    # normalize to a simple 'Good' / 'Bad' / 'Unknown' values
    def normalize_quality(val):
        try:
            s = str(val).strip().lower()
            if s in ("good", "g", "1", "yes", "y"):
                return "Good"
            if s in ("bad", "b", "0", "no", "n"):
                return "Bad"
            # allow phrases that contain good/bad
            if "good" in s:
                return "Good"
            if "bad" in s:
                return "Bad"
        except Exception:
            pass
        return "Unknown"

    df["Quality"] = df[quality_col].apply(normalize_quality)

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

# parse Date column so charts sort properly (keep original string if parsing fails)
def try_parse_date(s):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(str(s).strip(), fmt)
        except Exception:
            continue
    # fallback: try pandas
    try:
        return pd.to_datetime(s)
    except Exception:
        return pd.NaT

df["Date_parsed"] = df["Date"].apply(try_parse_date)
# for plotting keep a string label too (original)
df = df.sort_values("Date_parsed", na_position="last").reset_index(drop=True)

# --- Stats ---
if df["Duration (hrs)"].notna().any():
    st.metric("Average Sleep", f"{df['Duration (hrs)'].mean():.2f} hrs")
    st.metric("Total Sleep", f"{df['Duration (hrs)'].sum():.2f} hrs")

    # color mapping for qualities
    color_map = {"Good": "green", "Bad": "crimson", "Unknown": "lightgrey"}

    # --- Plotly Bar Chart (colored by Quality) ---
    st.subheader("Sleep Duration (Bar Chart) — colored by quality")
    # Use the parsed date for x if available, otherwise original Date strings
    x_col = "Date_parsed" if df["Date_parsed"].notna().any() else "Date"
    # when using Date_parsed, convert to string for nicer x-axis labels
    if x_col == "Date_parsed":
        df["_x_label"] = df["Date_parsed"].dt.strftime("%Y-%m-%d")
        x_col_plot = "_x_label"
    else:
        x_col_plot = "Date"

    fig_bar = px.bar(
        df,
        x=x_col_plot,
        y="Duration (hrs)",
        color="Quality",
        color_discrete_map=color_map,
        text="Duration (hrs)",
        title="Sleep Duration per Day",
        labels={"Duration (hrs)": "Hours Slept", x_col_plot: "Date"},
    )
    fig_bar.add_hline(
        y=8, line_dash="dash", line_color="red", annotation_text="Recommended 8 hrs"
    )
    fig_bar.update_traces(texttemplate="%{text}", textposition="outside")
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Plotly Line Chart (trend) ---
    st.subheader("Sleep Trend (Line Chart)")
    fig_line = px.line(
        df,
        x=x_col_plot,
        y="Duration (hrs)",
        markers=True,
        title="Sleep Trend Over Time",
        labels={"Duration (hrs)": "Hours Slept", x_col_plot: "Date"},
    )
    fig_line.add_hline(
        y=8, line_dash="dash", line_color="red", annotation_text="Recommended 8 hrs"
    )
    st.plotly_chart(fig_line, use_container_width=True)

else:
    st.info("No valid duration data found yet.")

# --- Show data ---
st.subheader("Sleep Log")
# show the normalized Quality and parsed Date for clarity
display_df = df.copy()
if "_x_label" in display_df.columns:
    display_df = display_df.rename(columns={"_x_label": "Date (parsed)"})
st.dataframe(display_df[["Date", "Date (parsed)" if "Date (parsed)" in display_df.columns else "Date_parsed", "Start", "End", "Duration (hrs)", "Quality"]], use_container_width=True)
