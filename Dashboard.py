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

url = "https://github.com/hornbyfp1-lang/Betting_App/blob/main/result_prediction.csv"

df = pd.read_csv(
    url,
    index_col=0,                                # because of the leading comma
    dayfirst=True,                              # 01-11-25 = 1 Nov 2025
    encoding="utf-8-sig"                        # robust to BOM
)

# (Optional) make column names friendlier
df.columns = [c.strip().replace(" - ", "_").replace(" ", "_") for c in df.columns]
# Example: "Home Win Probability - Prediction" -> "Home_Win_Probability_Prediction"


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


# In[ ]:










