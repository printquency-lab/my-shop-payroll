import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import base64

# --- 1. SETUP & BRANDING ---
st.set_page_config(page_title="Printquency", page_icon="logo.png")

col1, col2 = st.columns([1, 6]) 
with col1:
    try:
        st.image("logo.png", width=80) 
    except:
        pass

with col2:
    st.markdown("<h1 style='margin-top: -10px;'>Printquency Time Clock</h1>", unsafe_allow_html=True)

st.divider()

# --- 2. CONFIGURATION ---
HOURLY_RATE = 80.00
PH_TZ = pytz.timezone('Asia/Manila')

# IMPORTANT: Check that these IDs match your setup exactly
DEPLOYMENT_URL = "https://script.google.com/macros/s/AKfycbzx-yvh38TY7-6Ul9pSVJ9Hb-SNM19jJusS7KzhXC76eC2aTZBnzmeQZFhZmrWCGJVT/exec"
SHEET_ID = "1JAUdxkqV3CmCUZ8EGyhshI6AVhU_rJ1T9N7FE5-JmZM"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"
DRIVE_FOLDER_ID = "1_JL_SV709nwoFtTC7EJPoHYNcXF-1lvq"

# --- 3. SIDEBAR ADMIN ---
with st.sidebar:
    st.title("Settings")
    admin_mode = st.checkbox("Admin Access")
    admin_pw = ""
    if admin_mode:
        admin_pw = st.text_input("Enter Admin Password", type="password")

# --- 4. EMPLOYEE INTERFACE ---
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Employee Name:", names)
status = st.radio("Action:", ["Clock IN", "Clock OUT"], horizontal=True)

if name != "SELECT NAME":
    img = st.camera_input("Verify with Selfie")
    
    if img:
        now_ph = datetime.now(PH_TZ)
        date_str = now_ph.strftime("%Y-%m-%d")
        time_str = now_ph.strftime("%H:%M:%S")
        
        image_b64 = base64.b64encode(img.getvalue()).decode('utf-8')
        photo_name = f"{date_str}_{now_ph.strftime('%H%M')}_{name}_{status}.jpg"
        params = {"Date": date_str, "Time": time_str, "Employee": name, "Status": status, "Hours": "", "Pay": ""}

        try:
            # Load sheet to calculate math
            df = pd.read_csv(SHEET_CSV_URL)
            
            if status == "Clock OUT":
                # Find the open Clock IN for today
                match = df[(df['Date'] == date_str) & (df['Employee'] == name) & (df['Clock OUT'].isna())]
                if not match.empty:
                    t_in = pd.to_datetime(match.iloc[-1]['Clock IN'])
                    t_out = pd.to_datetime(time_str)
                    hrs = (t_out - t_in).total_seconds() / 3600
                    if hrs > 5: hrs -= 1 # Auto-lunch
                    params["Hours"] = round(hrs, 2)
                    params["Pay"] = f"₱{round(hrs * HOURLY_RATE, 2)}"

            # SUBMIT TO GOOGLE
            res = requests.get(DEPLOYMENT_URL, params=params, timeout=15)
            payload = {"image": image_b64, "filename": photo_name}
            requests.post(DEPLOYMENT_URL, json=payload, timeout=15)

            if "SYNC_OK" in res.text or "Success" in res.text:
                st.success(f"✅ {status} Synced!")
                st.balloons()
            else:
                st.warning("⚠️ Logged, but please check the sheet.")

        except Exception as e:
            st.error("Connection Error. Please verify your Web App URL.")

# --- 5. ADMIN PANEL ---
if st.query_params.get("view") == "hmaxine" or (admin_mode and admin_pw == "Hmaxine"):
    st.divider()
    st.subheader("🛡️ Manager Dashboard")
    try:
        # Re-fetch data for the dashboard
        df_admin = pd.read_csv(SHEET_CSV_URL)
        # Clean the 'Pay' column so it can be summed
        df_admin['Pay_Num'] = df_admin['Pay'].replace(r'[₱,]', '', regex=True).astype(float).fillna(0)
        
        st.metric(label="💰 Total Payroll Recorded", value=f"₱{round(df_admin['Pay_Num'].sum(), 2)}")
        st.dataframe(df_admin[['Date', 'Employee', 'Clock In', 'Clock OUT', 'Hours', 'Pay']])
        st.link_button("📂 Open Drive Photos", f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}")
    except:
        st.info("Dashboard waiting for data...")

