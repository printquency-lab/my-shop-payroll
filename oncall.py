import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. INITIAL SETUP
st.set_page_config(page_title="Printquency Payroll", page_icon="⏰")
HOURLY_RATE = 80.
