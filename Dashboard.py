#!/usr/bin/env python
# coding: utf-8

# ===== Imports =====
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from datetime import datetime
from zoneinfo import ZoneInfo  # stdlib; no pytz needed

st.set_page_config(page_title="Football Predictions Dashboard", layout="wide")
st.title("Football Predictions Dashboard")

RAW_URL = "https://raw.githubusercontent.com/hornbyfp1-lang/Betting_App/main/result_prediction.csv"

REQUIRED_COLS = [
    "Fixture", "Date of match",
    "Home Win Probability - Prediction", "Draw Probability - Prediction", "Away Win Probability - Prediction",
    "Home Win - Market Implied Probability", "Draw - Market Implied Probability", "Away Win - Market Implied Probability",
    "Home Win - Best Bookmaker Odds", "Draw - Best Bookmaker Odds", "Away Win- Best Bookmaker Odds",
    "Run date",
]

# ===== Data Loading (cached) =====
@st.cache_data(ttl=300)   # cache for 5 minutes
def load_data() -> pd.DataFrame:
    df = pd.read_csv(RAW_URL, sep=",", encoding="utf-8-sig", on_bad_lines="skip")
    # clean headers
    df.columns = df.columns.str.strip().str.replace("\ufeff", "", regex=False)

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # parse dates (keep as datetime for sorting/filtering)
    df["Date of match"] = pd.to_datetime(df["Date of match"], dayfirst=True, errors="coerce")
    df["Run date"] = pd.to_datetime(df["Run date"], errors="coerce")

    # coerce numeric probabilities
    prob_cols = [
        "Home Win Probability - Prediction", "Draw Probability - Prediction", "Away Win Probability - Prediction",
        "Home Win - Market Implied Probability", "Draw - Market Implied Probability", "Away Win - Market Implied Probability",
    ]
    df[prob_cols] = df[prob_cols].apply(pd.to_numeric, errors="coerce")
    return df

# ===== Manual refresh =====
col_btn, col_time = st.columns([1, 3], vertical_alignment="center")
with col_btn:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.experimental_rerun()

with col_time:
    now_uk = datetime.now(ZoneInfo("Europe/London"))
    st.caption(f"📅 Last refreshed: {now_uk:%Y-%m-%d %H:%M:%S %Z}")

df = load_data()

# ===== Sidebar Filters =====
fixture = st.sidebar.selectbox("Select fixture", df["Fixture"].dropna().unique())

# ===== Subset for chart =====
row = df.loc[df["Fixture"] == fixture].head(1)
if row.empty:
    st.warning("No data for the selected fixture.")
    st.stop()

plot_df = pd.DataFrame({
    "Outcome": ["Home Win", "Draw", "Away Win"] * 2,
    "Probability": [
        float(row["Home Win Probability - Prediction"].iloc[0]),
        float(row["Draw Probability - Prediction"].iloc[0]),
        float(row["Away Win Probability - Prediction"].iloc[0]),
        float(row["Home Win - Market Implied Probability"].iloc[0]),
        float(row["Draw - Market Implied Probability"].iloc[0]),
        float(row["Away Win - Market Implied Probability"].iloc[0]),
    ],
    "Source": ["Prediction"] * 3 + ["Market"] * 3,
})

fig = px.bar(
    plot_df, x="Outcome", y="Probability", color="Source",
    barmode="group", text_auto=".2%",
    title=f"Predicted vs Market Probabilities — {fixture}",
)
fig.update_yaxes(tickformat=".0%")
st.plotly_chart(fig, use_container_width=True)

# ===== Table (pretty dates) =====
st.subheader("All fixtures")
st.dataframe(
    df.sort_values(["Date of match", "Fixture"]).reset_index(drop=True),
    use_container_width=True,
    column_config={
        "Date of match": st.column_config.DateColumn("Date of match", format="DD-MM-YYYY"),
        "Run date": st.column_config.DatetimeColumn("Run date", format="DD-MM-YYYY HH:mm"),
    },
)
