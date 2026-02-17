import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. SETUP & THEME
st.set_page_config(page_title="Printquency Payroll", page_icon="⏰")
HOURLY_RATE = 80.00 

# This is your new shop header
st.header("🖨️ Printquency Time Clock", divider="blue")

# 2. SELECTION
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
selected_name = st.selectbox("Select Employee:", names)

# Using columns to make the IN/OUT buttons look better on mobile
col1, col2
