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

    # Ch
