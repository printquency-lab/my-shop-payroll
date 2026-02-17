import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import base64

# --- CONFIG ---
st.set_page_config(page_title="Printquency", page_icon="⏰")
HOURLY_RATE = 80.00
PH_TZ = pytz.timezone('Asia/Manila')

DEPLOYMENT_URL = "https://script.google.com/macros/s/AKfycbzvT7GP6ZdFkk_WeyvDQEI1Bm892n-fd7C593nHfeJuvOdx-R99x2YyXlTAKM9ZrkINAA/exec"
SHEET_ID = "1JAUdxkqV3CmCUZ8EGyhshI6AVhU_rJ1T9N7FE5-JmZM"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.header("🖨️ Printquency Time Clock", divider="blue")

# --- UI ---
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Employee Name:", names)
status = st.radio("Action:", ["Clock IN", "Clock OUT"], horizontal=True)

if name != "SELECT NAME":
    img = st.camera_input("Verify with Selfie")
    
    if img:
        now_ph = datetime.now(PH_TZ)
        date_str = now_ph.strftime("%Y-%m-%d")
        time_str = now_ph.strftime("%H:%M:%S")
        
        # Prepare Photo
        image_b64 = base64.b64encode(img.getvalue()).decode('utf-8')
        photo_name = f"{date_str}_{now_ph.strftime('%H%M')}_{name}_{status}.jpg"

        params = {"Date": date_str, "Time": time_str, "Employee": name, "Status": status, "Hours": "", "Pay": ""}

        if status == "Clock OUT":
            try:
                df = pd.read_csv(SHEET_CSV_URL)
                # Find matching IN
                match = df[(df['Date'] == date_str) & (df['Employee'] == name) & (df['Clock OUT'].isna())]
                if not match.empty:
                    t_in = pd.to_datetime(match.iloc[-1]['Clock IN'])
                    hrs = (pd.to_datetime(time_str) - t_in).total_seconds() / 3600
                    if hrs > 5: hrs -= 1 # 1-Hour Lunch Rule
                    params["Hours"] = round(hrs, 2)
                    params["Pay"] = f"₱{round(hrs * HOURLY_RATE, 2)}"
            except: pass

        try:
            # Send Data to Sheet and Photo to Drive
            requests.get(DEPLOYMENT_URL, params=params)
            requests.post(DEPLOYMENT_URL, data={"image": image_b64, "filename": photo_name})
            st.success(f"✅ {status} Logged! Hello, {name}.")
            st.balloons()
        except:
            st.error("Connection failed. Check your Web App URL.")

# --- ADMIN ---
st.divider()
with st.expander("🛡️ Admin Panel"):
    pw = st.text_input("Password", type="password")
    if pw == "Hmaxine":
        try:
            df = pd.read_csv(SHEET_CSV_URL)
            st.dataframe(df)
            st.link_button("📂 View Photos in Drive", "PASTE_YOUR_DRIVE_FOLDER_LINK_HERE")
        except: st.info("No records yet.")
