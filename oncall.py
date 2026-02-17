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
        st.error("Error: 'logo.png' not found.")

with col2:
    st.markdown("<h1 style='margin-top: -10px;'>Printquency Time Clock</h1>", unsafe_allow_html=True)

st.divider()

# --- 2. CONFIGURATION ---
HOURLY_RATE = 80.00
PH_TZ = pytz.timezone('Asia/Manila')

# Replace these with your actual IDs
DEPLOYMENT_URL = "https://script.google.com/macros/s/AKfycbx5T84TMKi1tD0Tdwhpg46PVX_E1JQ9uU-S0sBKlSANYWWjRV4aYWIPYzQ8gviQH95szg/exec"
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
            # 1. Load data to check status
            df_check = pd.read_csv(SHEET_CSV_URL)
            
            # 2. Anti-Duplicate Check
            last_entry = df_check[(df_check['Employee'] == name) & (df_check['Date'] == date_str)].tail(1)
            is_duplicate = False
            if not last_entry.empty and last_entry.iloc[0]['Status'] == status:
                st.warning(f"⚠️ Action already recorded! You are already {status}ed.")
                is_duplicate = True

            if not is_duplicate:
                # 3. Clock Out Math
                if status == "Clock OUT":
                    match = df_check[(df_check['Date'] == date_str) & (df_check['Employee'] == name) & (df_check['Clock OUT'].isna())]
                    if not match.empty:
                        t_in = pd.to_datetime(match.iloc[-1]['Clock IN'])
                        t_out = pd.to_datetime(time_str)
                        hrs = (t_out - t_in).total_seconds() / 3600
                        if hrs > 5: hrs -= 1 # Auto-Lunch Deduction
                        params["Hours"] = round(hrs, 2)
                        params["Pay"] = f"₱{round(hrs * HOURLY_RATE, 2)}"

                # 4. Submit to Google
                requests.get(DEPLOYMENT_URL, params=params, timeout=15)
                requests.post(DEPLOYMENT_URL, data={"image": image_b64, "filename": photo_name}, timeout=15)
                
                # 5. Success UI
                if status == "Clock IN":
                    st.success(f"⚡ Welcome, {name}!")
                else:
                    st.success(f"🏁 Great work, {name}!")
                st.balloons()

        except Exception as e:
            st.error("Connection error. Please refresh and try again.")

# --- 5. ADMIN PANEL ---
if st.query_params.get("view") == "hmaxine" or (admin_mode and admin_pw == "Hmaxine"):
    st.divider()
    st.subheader("🛡️ Manager Dashboard")
    try:
        df = pd.read_csv(SHEET_CSV_URL)
        df['Pay_Num'] = df['Pay'].replace(r'[₱,]', '', regex=True).astype(float).fillna(0)
        df['Date_Obj'] = pd.to_datetime(df['Date'])
        
        st.metric(label="💰 Grand Total Payroll", value=f"₱{round(df['Pay_Num'].sum(), 2)}")
        
        st.link_button("📂 Open Drive Photos", f"https://drive.google.com/drive/folders/{DRIVE_FOLDER_ID}")
    except:
        st.info("Awaiting records...")
