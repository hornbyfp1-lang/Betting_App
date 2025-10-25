#!/usr/bin/env python
# coding: utf-8

# In[16]:


#Data Manipulation
import pandas as pd
from pandas import json_normalize
#Scraping
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
#Time
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import BDay
#Maths
import numpy as np
from scipy.stats import poisson

import re

#APP FRONT-END
import streamlit as st

import plotly.express as px


# In[24]:


import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Football Predictions Dashboard")

# Load data
import pandas as pd

url = "https://raw.githubusercontent.com/hornbyfp1-lang/Betting_App/main/result_prediction.csv"

must_have = [
    "Fixture","Date of match",
    "Home Win Probability - Prediction","Draw Probability - Prediction","Away Win Probability - Prediction",
    "Home Win - Market Implied Probability","Draw - Market Implied Probability","Away Win - Market Implied Probability",
    "Home Win - Best Bookmaker Odds","Draw - Best Bookmaker Odds","Away Win- Best Bookmaker Odds","Run date"
]

# Load
df = pd.read_csv(
    url,
    sep=",",
    encoding="utf-8-sig",
    on_bad_lines="skip"  # skips any truncated/garbage lines
)

# Column hygiene
df.columns = df.columns.str.strip().str.replace("\ufeff", "", regex=False)

# Ensure required columns exist
missing = [c for c in must_have if c not in df.columns]
if missing:
    raise ValueError(f"Missing columns: {missing}. Check the CSV header / delimiters.")

# Parse dates
df["Date of match"] = pd.to_datetime(df["Date of match"], dayfirst=True, errors="coerce")
df["Run date"] = pd.to_datetime(df["Run date"], errors="coerce")

# Coerce numeric probability columns
prob_cols = [
    "Home Win Probability - Prediction","Draw Probability - Prediction","Away Win Probability - Prediction",
    "Home Win - Market Implied Probability","Draw - Market Implied Probability","Away Win - Market Implied Probability",
]
df[prob_cols] = df[prob_cols].apply(pd.to_numeric, errors="coerce")

# Quick sanity checks
assert df["Fixture"].notna().all(), "Some rows have missing Fixture."
assert df["Date of match"].notna().any(), "No dates parsed — check date format (should be DD-MM-YY)."

# Sidebar filter
fixture_selection = st.sidebar.selectbox("Select fixture", df["Fixture"].unique())

# Filter data
filtered_df = df[df["Fixture"] == fixture_selection]

# Prepare data for plotting
plot_df = pd.DataFrame({
    "Outcome": ["Home Win", "Draw", "Away Win"] * 2,
    "Probability": [
        filtered_df["Home Win Probability - Prediction"].values[0],
        filtered_df["Draw Probability - Prediction"].values[0],
        filtered_df["Away Win Probability - Prediction"].values[0],
        filtered_df["Home Win - Market Implied Probability"].values[0],
        filtered_df["Draw - Market Implied Probability"].values[0],
        filtered_df["Away Win - Market Implied Probability"].values[0],
    ],
    "Source": ["Prediction"] * 3 + ["Market"] * 3
})

# Plot
fig = px.bar(
    plot_df,
    x="Outcome",
    y="Probability",
    color="Source",
    barmode="group",
    title=f"Predicted vs Market Probabilities for {fixture_selection}",
    text_auto=True
)
st.plotly_chart(fig)

# Optional: Show raw data
with st.expander("Show raw data"):
    st.dataframe(filtered_df)

import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)  # cache for 5 minutes (or whatever you like)
def load_data():
    url = "https://raw.githubusercontent.com/hornbyfp1-lang/Betting_App/main/result_prediction.csv"
    df = pd.read_csv(url, encoding="utf-8-sig")
    df.columns = df.columns.str.strip().str.replace("\ufeff", "")
    df["Date of match"] = pd.to_datetime(df["Date of match"], dayfirst=True, errors="coerce")
    df["Run date"] = pd.to_datetime(df["Run date"], errors="coerce")
    return df

# 👇 Manual refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

df = load_data()

from datetime import datetime
import pytz

uk_tz = pytz.timezone("Europe/London")
now_uk = datetime.now(uk_tz)

st.caption(f"📅 Last refreshed: {now_uk:%Y-%m-%d %H:%M:%S %Z}")

st.dataframe(df)

# In[ ]:

















