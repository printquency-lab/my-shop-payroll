import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import base64

# --- 1. SETUP & BRANDING ---
# page_icon sets the browser tab icon
st.set_page_config(page_title="Printquency", page_icon="logo.png")

# Displays your logo at the top
st.image("logo.png", width=150) 
st.header("Printquency Time Clock", divider="blue")

# --- 2. CONFIGURATION ---
HOURLY_RATE = 80.00
PH_TZ = pytz.timezone('Asia/Manila')

# Replace these with your actual links/IDs
DEPLOYMENT_URL = "PASTE_YOUR_WEB_APP_URL_HERE"
SHEET_ID = "1JAUdxkqV3CmCUZ8EGyhshI6AVhU_rJ1T9N7FE5-JmZM"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# --- 3. EMPLOYEE INTERFACE ---
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Employee Name:", names)
status = st.radio("Action:", ["Clock IN", "Clock OUT"], horizontal=True)

if name != "SELECT NAME":
    img = st.camera_input("Verify with Selfie")
    
    if img:
        now_ph = datetime.now(PH_TZ)
        date_str = now_ph.strftime("%Y-%m-%d")
        time_str = now_ph.strftime("%H:%M:%S")
        
        # Prepare Photo for Google Drive
        image_b64 = base64.b64encode(img.getvalue()).decode('utf-8')
        photo_name = f"{date_str}_{now_ph.strftime('%H%M')}_{name}_{status}.jpg"

        params = {
            "Date": date_str, "Time": time_str, 
            "Employee": name, "Status": status, 
            "Hours": "", "Pay": ""
        }

        # Calculate Payroll Logic on Clock OUT
        if status == "Clock OUT":
            try:
                df = pd.read_csv(SHEET_CSV_URL)
                match = df[(df['Date'] == date_str) & (df['Employee'] == name) & (df['Clock OUT'].isna())]
                if not match.empty:
                    # pd.to_datetime handles 24-hour math correctly
                    t_in = pd.to_datetime(match.iloc[-1]['Clock IN'])
                    t_out = pd.to_datetime(time_str)
                    hrs = (t_out - t_in).total_seconds() / 3600
                    
                    # 1-Hour Lunch Rule for shifts over 5 hours
                    if hrs > 5:
                        hrs -= 1
                    
                    params["Hours"] = round(hrs, 2)
                    params["Pay"] = f"₱{round(hrs * HOURLY_RATE, 2)}"
            except:
                pass

        # Send Data to Sheets & Photo to Drive
        try:
            requests.get(DEPLOYMENT_URL, params=params)
            requests.post(DEPLOYMENT_URL, data={"image": image_b64, "filename": photo_name})
            st.success(f"✅ {status} Logged! Time: {now_ph.strftime('%I:%M %p')}")
            st.balloons()
        except:
            st.error("Connection failed. Check your Deployment URL.")

# --- 4. ADMIN PANEL ---
st.divider()
with st.expander("🛡️ Admin Panel"):
    pw = st.text_input("Password", type="password")
    if pw == "Hmaxine":
        try:
            df = pd.read_csv(SHEET_CSV_URL)
            if 'Pay' in df.columns:
                total_val = df['Pay'].replace(r'[₱,]', '', regex=True).astype(float).sum()
                st.metric(label="💰 Grand Total Payroll", value=f"₱{round(total_val, 2)}")
            st.dataframe(df)
        except:
            st.info("Awaiting records...")
