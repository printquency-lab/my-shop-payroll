import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz  # This is the "Timezone" library

# 1. SETUP & GSHEET CONNECTION
st.set_page_config(page_title="Printquency", page_icon="⏰")
HOURLY_RATE = 80.00

# Set the Timezone to Philippines
PH_TZ = pytz.timezone('Asia/Manila')

# YOUR LINKS
DEPLOYMENT_URL = "https://script.google.com/macros/s/AKfycbyBHAwzfzr6nm5uEInSXpGRmZjQIL1XxiSJC-saM3ngHmIqsvp4nAIQkxJSXCVDvYwiUg/exec"
SHEET_ID = "1JAUdxkqV3CmCUZ8EGyhshI6AVhU_rJ1T9N7FE5-JmZM"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.header("🖨️ Printquency Time Clock", divider="blue")

# 2. EMPLOYEE INTERFACE
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Employee Name:", names)
status = st.radio("Action:", ["Clock IN", "Clock OUT"], horizontal=True)

if name != "SELECT NAME":
    img = st.camera_input("Verify with Selfie")
    
    if img:
        # --- THIS IS THE TIME FIX ---
        now_ph = datetime.now(PH_TZ) # Gets Manila Time
        date_str = now_ph.strftime("%Y-%m-%d")
        time_str = now_ph.strftime("%H:%M:%S")
        
        params = {
            "Date": date_str,
            "Time": time_str,
            "Employee": name,
            "Status": status
        }
        
        try:
            response = requests.get(DEPLOYMENT_URL, params=params, timeout=10)
            if "Success" in response.text:
                st.success(f"✅ Logged at {time_str} (PH Time)!")
                st.balloons()
        except:
            st.error("Error connecting to Google Sheets.")

# 3. ADMIN PANEL
st.divider()
with st.expander("🛡️ Admin Panel"):
    pw = st.text_input("Password", type="password")
    if pw == "Hmaxine":
        try:
            df = pd.read_csv(SHEET_CSV_URL)
            st.write(f"### Pay Summary (₱{HOURLY_RATE}/hr)")
            
            # (Keep your math logic here)
            st.dataframe(df)
        except:
            st.info("Check your Sheet sharing settings.")

