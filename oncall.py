import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz
import base64

# --- SETUP ---
st.set_page_config(page_title="Printquency", page_icon="logo.png")
HOURLY_RATE = 80.00
PH_TZ = pytz.timezone('Asia/Manila')

DEPLOYMENT_URL = "https://script.google.com/macros/s/AKfycbxRbDw8q0icMDiS4joSLasK1twqsoOSRDbFpmWnDBUGuefgbbGb28cj8xP4qdxRFQ9xGw/exec"
SHEET_ID = "1JAUdxkqV3CmCUZ8EGyhshI6AVhU_rJ1T9N7FE5-JmZM"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.title("Printquency Time Clock")

# --- INTERFACE ---
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Employee Name:", names)
status = st.radio("Action:", ["Clock IN", "Clock OUT"], horizontal=True)

if name != "SELECT NAME":
    img = st.camera_input("Verify Identity")
    if img:
        now = datetime.now(PH_TZ)
        dt, tm = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
        params = {"Date": dt, "Time": tm, "Employee": name, "Status": status, "Hours": "", "Pay": ""}
        
        try:
            # 1. Math for Clock OUT
            df = pd.read_csv(SHEET_CSV_URL)
            if status == "Clock OUT":
                match = df[(df['Date'] == dt) & (df['Employee'] == name) & (df['Clock OUT'].isna())]
                if not match.empty:
                    # Case sensitive column check
                    col_name = 'Clock In' if 'Clock In' in df.columns else 'Clock IN'
                    t_in = pd.to_datetime(match.iloc[-1][col_name])
                    hrs = (pd.to_datetime(tm) - t_in).total_seconds() / 3600
                    if hrs > 5: hrs -= 1
                    params["Hours"], params["Pay"] = round(hrs, 2), f"₱{round(hrs * HOURLY_RATE, 2)}"

            # 2. PRIORITY: Sync Data to Sheet
            res = requests.get(DEPLOYMENT_URL, params=params, timeout=15)
            
            if "SYNC_OK" in res.text:
                st.success(f"✅ {status} Synced to Sheet!")
                # 3. SECONDARY: Attempt Photo Upload
                img_b64 = base64.b64encode(img.getvalue()).decode()
                requests.post(DEPLOYMENT_URL, json={"image": img_b64, "filename": f"{dt}_{name}.jpg"}, timeout=10)
                st.balloons()
            else:
                st.error(f"❌ Google Error: {res.text}")
        except Exception as e:
            st.error(f"Connection Error: {e}")

# --- DASHBOARD ---
st.divider()
st.subheader("🛡️ Manager Dashboard")
if st.button("📧 Send Weekly Payroll Report"):
    r = requests.get(DEPLOYMENT_URL, params={"Action": "SendReport"})
    st.success("Report Sent!") if "REPORT_SENT" in r.text else st.error("Failed.")

try:
    df_db = pd.read_csv(SHEET_CSV_URL)
    st.dataframe(df_db)
except:
    st.info("Awaiting data...")
