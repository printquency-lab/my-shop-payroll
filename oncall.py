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

# IMPORTANT: Double-check these three IDs
DEPLOYMENT_URL = "https://script.google.com/macros/s/AKfycbxRbDw8q0icMDiS4joSLasK1twqsoOSRDbFpmWnDBUGuefgbbGb28cj8xP4qdxRFQ9xGw/exec"
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
        
        image_b64 = base64.b64encode(img.getvalue()).decode('utf-8')
        photo_name = f"{date_str}_{now_ph.strftime('%H%M')}_{name}_{status}.jpg"
        params = {"Date": date_str, "Time": time_str, "Employee": name, "Status": status, "Hours": "", "Pay": ""}

        try:
            # 1. Fetch current data for math
            df = pd.read_csv(SHEET_CSV_URL)
            
            if status == "Clock OUT":
                # Find Adam/Mark's current session
                match = df[(df['Date'] == date_str) & (df['Employee'] == name) & (df['Clock OUT'].isna())]
                if not match.empty:
                    t_in = pd.to_datetime(match.iloc[-1]['Clock IN'])
                    t_out = pd.to_datetime(time_str)
                    hrs = (t_out - t_in).total_seconds() / 3600
                    if hrs > 5: hrs -= 1 # Auto-Lunch
                    params["Hours"] = round(hrs, 2)
                    params["Pay"] = f"₱{round(hrs * HOURLY_RATE, 2)}"

            # 2. Submit to Google
            res = requests.get(DEPLOYMENT_URL, params=params, timeout=15)
            payload = {"image": image_b64, "filename": photo_name}
            requests.post(DEPLOYMENT_URL, json=payload, timeout=15)

            if "SYNC_OK" in res.text or "Success" in res.text:
                st.success(f"✅ {status} Synced! Data is safe.")
                st.balloons()
            else:
                st.warning("⚠️ Data sent, but check sheet for Pay calculation.")

        except Exception as e:
            st.error(f"Error: {e}. Please check your Web App URL deployment.")

# --- 4. MANAGER DASHBOARD ---
st.divider()
st.subheader("🛡️ Manager Dashboard")
try:
    df_admin = pd.read_csv(SHEET_CSV_URL)
    # This part shows the money again
    df_admin['Pay_Num'] = df_admin['Pay'].replace(r'[₱,]', '', regex=True).astype(float).fillna(0)
    st.metric(label="💰 Total Payroll Recorded", value=f"₱{round(df_admin['Pay_Num'].sum(), 2)}")
    st.dataframe(df_admin)
except:
    st.info("Waiting for first entry to load dashboard...")

