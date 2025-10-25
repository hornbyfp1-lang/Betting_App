#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations

# ---- App setup ----
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import streamlit as st

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

NUMERIC_PROB_COLS = [
    "Home Win Probability - Prediction", "Draw Probability - Prediction", "Away Win Probability - Prediction",
    "Home Win - Market Implied Probability", "Draw - Market Implied Probability", "Away Win - Market Implied Probability",
]


# ---- Data loader (cached) ----
@st.cache_data(ttl=300)  # keep for 5 minutes
def load_data(cache_buster: int) -> pd.DataFrame:
    """
    Load and sanitize the CSV from GitHub.
    cache_buster is used to make the cache key change over time and bust any upstream CDN cache.
    """
    # add a query param so raw.githubusercontent.com/CDN is less likely to hand us an old copy
    url = f"{RAW_URL}?nocache={cache_buster}"

    df = pd.read_csv(
        url,
        sep=",",
        encoding="utf-8-sig",
        on_bad_lines="skip"  # skip any malformed lines
    )

    # Clean header noise (e.g., BOM)
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\ufeff", "", regex=False)
    )

    # Check required columns
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    # Parse dates (keep originals for display formatting below)
    df["Date of match"] = pd.to_datetime(df["Date of match"], dayfirst=True, errors="coerce")
    df["Run date"] = pd.to_datetime(df["Run date"], errors="coerce")

    # Convert probabilities to numeric
    df[NUMERIC_PROB_COLS] = df[NUMERIC_PROB_COLS].apply(pd.to_numeric, errors="coerce")

    # Display-friendly date strings (DD-MM-YYYY)
    df["Date of match"] = df["Date of match"].dt.strftime("%d-%m-%Y")
    df["Run date"] = df["Run date"].dt.strftime("%d-%m-%Y")

    return df


# ---- Controls / refresh ----
left, right = st.columns([1, 4])
with left:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# cache_buster changes every minute → new cache entry + new raw URL query param
cache_buster = int(time.time() // 60)

# Load data safely
try:
    df = load_data(cache_buster)
except Exception as e:
    st.error(f"Failed to load data: {e}")
    st.stop()

# Last refreshed label (London time)
now_uk = datetime.now(ZoneInfo("Europe/London"))
with right:
    st.caption(f"🗓️ Last refreshed: {now_uk:%Y-%m-%d %H:%M:%S %Z}")

# ---- Sidebar filters ----
with st.sidebar:
    st.header("Filters")
    fixtures = df["Fixture"].dropna().unique()
    fixture_selection = st.selectbox("Select a fixture", fixtures)

# ---- Main view: table + chart ----
filtered = df[df["Fixture"] == fixture_selection].copy()
if filtered.empty:
    st.warning("No rows found for that fixture.")
else:
    # Show the data table (displaying formatted date columns)
    display_cols = [
        "Fixture",
        "Date of match",
        "Home Win Probability - Prediction", "Draw Probability - Prediction", "Away Win Probability - Prediction",
        "Home Win - Market Implied Probability", "Draw - Market Implied Probability", "Away Win - Market Implied Probability",
        "Home Win - Best Bookmaker Odds", "Draw - Best Bookmaker Odds", "Away Win- Best Bookmaker Odds",
        "Run date",
    ]
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)

    # Build chart data (use the first row of the selection)
    row = filtered.iloc[0]
    plot_df = pd.DataFrame({
        "Outcome": ["Home Win", "Draw", "Away Win"] * 2,
        "Probability": [
            row["Home Win Probability - Prediction"],
            row["Draw Probability - Prediction"],
            row["Away Win Probability - Prediction"],
            row["Home Win - Market Implied Probability"],
            row["Draw - Market Implied Probability"],
            row["Away Win - Market Implied Probability"],
        ],
        "Source": ["Prediction"] * 3 + ["Market"] * 3,
    })

    fig = px.bar(
        plot_df,
        x="Outcome",
        y="Probability",
        color="Source",
        barmode="group",
        title=f"Predicted vs Market Probabilities — {fixture_selection}",
        text_auto=".1%"
    )
    fig.update_yaxes(range=[0, 1], tickformat=".0%")
    fig.update_layout(legend_title_text="", yaxis_title="Probability", xaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

