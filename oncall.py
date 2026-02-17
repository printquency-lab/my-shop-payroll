import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Printquency", page_icon="⏰")
HOURLY_RATE = 80.00
PH_TZ = pytz.timezone('Asia/Manila')

DEPLOYMENT_URL = "https://script.google.com/macros/s/AKfycby0k22aSbEkwHi3-D2FBES2C49JnRhjNk-tZDOaukbnIpFNrm0oWlNOJzAe7Tl96H4peg/exec"
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
        
        # PREPARE PHOTO FOR GOOGLE DRIVE
        image_bytes = img.getvalue()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')
        photo_filename = f"{date_str}_{now_ph.strftime('%H%M')}_{name}_{status}.jpg"

        # A. SEND LOG TO SHEET (GET REQUEST)
        params = {"Date": date_str, "Time": time_str, "Employee": name, "Status": status, "Hours": "", "Pay": ""}

        if status == "Clock OUT":
            try:
                df = pd.read_csv(SHEET_CSV_URL)
                today_in = df[(df['Date'] == date_str) & (df['Employee'] == name) & (df['Clock OUT'].isna())]
                if not today_in.empty:
                    t_in = pd.to_datetime(today_in.iloc[-1]['Clock IN'])
                    hrs = (pd.to_datetime(time_str) - t_in).total_seconds() / 3600
                    if hrs > 5: hrs -= 1 
                    params["Hours"] = round(hrs, 2)
                    params["Pay"] = f"₱{round(hrs * HOURLY_RATE, 2)}"
            except: pass

        # B. SEND PHOTO TO DRIVE (POST REQUEST)
        try:
            requests.get(DEPLOYMENT_URL, params=params) # Logs data
            requests.post(DEPLOYMENT_URL, data={"image": image_b64, "filename": photo_filename}) # Saves photo
            st.success(f"✅ {status} Logged! Photo saved to Secure Drive.")
            st.balloons()
        except:
            st.error("Connection Error.")

# --- 3. ADMIN PANEL ---
st.divider()
with st.expander("🛡️ Admin Panel"):
    pw = st.text_input("Password", type="password")
    if pw == "Hmaxine":
        try:
            df = pd.read_csv(SHEET_CSV_URL)
            st.write(f"### Pay Summary (₱{HOURLY_RATE}/hr)")
            st.dataframe(df)
            st.link_button("📂 View All Photos in Drive", f"https://drive.google.com/drive/folders/PASTE_YOUR_FOLDER_ID_HERE")
        except: st.info("No records found.")
