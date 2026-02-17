import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import base64

# --- 1. SETUP & BRANDING ---
st.set_page_config(page_title="Printquency", page_icon="logo.png")

# Logo and Title Alignment
col1, col2 = st.columns([1, 6]) 
with col1:
    try:
        st.image("logo.png", width=80) 
    except:
        st.error("Error: 'logo.png' not found in GitHub.")

with col2:
    st.markdown("<h1 style='margin-top: -10px;'>Printquency Time Clock</h1>", unsafe_allow_html=True)

st.divider()

# --- 2. CONFIGURATION ---
HOURLY_RATE = 80.00
PH_TZ = pytz.timezone('Asia/Manila')

# Replace these with your actual IDs/Links
DEPLOYMENT_URL = "PASTE_YOUR_LATEST_WEB_APP_URL_HERE"
SHEET_ID = "1JAUdxkqV3CmCUZ8EGyhshI6AVhU_rJ1T9N7FE5-JmZM"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
DRIVE_FOLDER_ID = "1_JL_SV709nwoFtTC7EJPoHYNcXF-1lvq"

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
        
        # Prepare Photo Data
        image_b64 = base64.b64encode(img.getvalue()).decode('utf-8')
        photo_name = f"{date_str}_{now_ph.strftime('%H%M')}_{name}_{status}.jpg"

        params = {"Date": date_str, "Time": time_str, "Employee": name, "Status": status, "Hours": "", "Pay": ""}

        if status == "Clock OUT":
            try:
                df = pd.read_csv(SHEET_CSV_URL)
                match = df[(df['Date'] == date_str) & (df['Employee'] == name) & (df['Clock OUT'].isna())]
                if not match.empty:
                    t_in = pd.to_datetime(match.iloc[-1]['Clock IN'])
                    hrs = (pd.to_datetime(time_str) - t_in).total_seconds() / 3600
                    if hrs > 5: hrs -= 1 # 1-Hour Lunch Rule
                    params["Hours"] = round(hrs, 2)
                    params["Pay"] = f"₱{round(hrs * HOURLY_RATE, 2)}"
            except: pass

        try:
            # Send Data to Sheets and Photo to Drive
            requests.get(DEPLOYMENT_URL, params=params)
            requests.post(DEPLOYMENT_URL, data={"image": image_b64, "filename": photo_name})
            st.success(f"✅ {status} Logged! Time: {now_ph.strftime('%I:%M %p')}")
            st.balloons()
        except:
            st.error("Connection failed. Check your Web App URL.")

# --- 4. HIDDEN ADMIN PANEL (?view=hmaxine) ---
if st.query_params.get("view") == "hmaxine":
    st.divider()
    st.subheader("🛡️ Manager Dashboard")
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        if 'Pay' in df.columns:
            total_val = df['Pay'].replace(r'[₱,]', '', regex=True).astype(float).sum()
            st.metric(label="💰 Total Payroll to Date", value=f"₱{round(total_val, 2)}")
        
        st.dataframe(df)

        # Download CSV Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Payroll CSV",
            data=csv,
            file_name=f"Payroll_{date_str}.csv",
            mime="text/csv",
        )
        st.link_button("📂 Open Google Drive Photos", f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}")
    except:
        st.info("Awaiting records...")
