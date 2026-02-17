import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Printquency", page_icon="⏰")
HOURLY_RATE = 80.00
PH_TZ = pytz.timezone('Asia/Manila')

# PASTE YOUR LINKS HERE
DEPLOYMENT_URL = "https://script.google.com/macros/s/AKfycbz2hqTkkS6eslGlcrBQHIGYC72F42iNk7k2alQHlvC43iEKlDbg1LsI4DSDwnsc4ZtMow/exec"
SHEET_ID = "1JAUdxkqV3CmCUZ8EGyhshI6AVhU_rJ1T9N7FE5-JmZM"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.header("🖨️ Printquency Time Clock", divider="blue")

# --- 2. EMPLOYEE INTERFACE ---
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Employee Name:", names)
status = st.radio("Action:", ["Clock IN", "Clock OUT"], horizontal=True)

if name != "SELECT NAME":
    img = st.camera_input("Verify with Selfie")
    
    if img:
        now_ph = datetime.now(PH_TZ)
        date_str = now_ph.strftime("%Y-%m-%d")
        time_str = now_ph.strftime("%H:%M:%S")
        
        params = {
            "Date": date_str, "Time": time_str, 
            "Employee": name, "Status": status,
            "Hours": "", "Pay": ""
        }

        # CALCULATE PAYROLL DATA ON CLOCK OUT
        if status == "Clock OUT":
            try:
                df = pd.read_csv(SHEET_CSV_URL)
                # Find the most recent "IN" for today that hasn't been closed
                today_in = df[(df['Date'] == date_str) & (df['Employee'] == name) & (df['Clock OUT'].isna())]
                
                if not today_in.empty:
                    t_in = pd.to_datetime(today_in.iloc[-1]['Clock IN'])
                    t_out = pd.to_datetime(time_str)
                    hrs = (t_out - t_in).total_seconds() / 3600
                    
                    if hrs > 5: hrs -= 1 # 1-Hour Lunch Rule
                    
                    params["Hours"] = round(hrs, 2)
                    params["Pay"] = f"₱{round(hrs * HOURLY_RATE, 2)}"
            except:
                st.warning("Could not calculate pay in real-time, but logging time...")

        # SEND TO GOOGLE SHEETS
        try:
            resp = requests.get(DEPLOYMENT_URL, params=params, timeout=10)
            if "Success" in resp.text:
                st.success(f"✅ {status} Logged! Time: {now_ph.strftime('%I:%M %p')}")
                st.balloons()
            else:
                st.error(f"Sheet Error: {resp.text}")
        except:
            st.error("Connection failed. Check your Web App URL.")

# --- 3. ADMIN PANEL ---
st.divider()
with st.expander("🛡️ Admin Panel"):
    pw = st.text_input("Password", type="password")
    if pw == "Hmaxine":
        try:
            df = pd.read_csv(SHEET_CSV_URL)
            st.write(f"### Pay Summary (₱{HOURLY_RATE}/hr)")
            
            # Show live calculation of Grand Total
            if 'Pay' in df.columns:
                # Clean currency symbol to sum values
                total_val = df['Pay'].replace(r'[₱,]', '', regex=True).astype(float).sum()
                st.metric(label="💰 Grand Total Payroll", value=f"₱{round(total_val, 2)}")
            
            st.dataframe(df)
            st.link_button("📂 Open Google Sheet", f
