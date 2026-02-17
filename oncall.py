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

# Update with your latest Deployment URL
DEPLOYMENT_URL = "https://script.google.com/macros/s/AKfycbxRbDw8q0icMDiS4joSLasK1twqsoOSRDbFpmWnDBUGuefgbbGb28cj8xP4qdxRFQ9xGw/exec"
SHEET_ID = "1JAUdxkqV3CmCUZ8EGyhshI6AVhU_rJ1T9N7FE5-JmZM"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.title("Printquency Time Clock")

# --- 1. SIDEBAR ADMIN (Hidden Logic) ---
with st.sidebar:
    st.title("Settings")
    admin_mode = st.checkbox("Admin Access")
    admin_pw = ""
    if admin_mode:
        admin_pw = st.text_input("Enter Admin Password", type="password")

# --- 2. EMPLOYEE INTERFACE ---
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Employee Name:", names)
status = st.radio("Action:", ["Clock IN", "Clock OUT"], horizontal=True)

if name != "SELECT NAME":
    img = st.camera_input("Verify Identity")
    if img:
        now = datetime.now(PH_TZ)
        dt, tm = now.strftime("%Y-%m-%d"), now.strftime("%I:%M:%S %p")
        params = {"Date": dt, "Time": tm, "Employee": name, "Status": status, "Hours": "", "Pay": ""}
        
        try:
            df = pd.read_csv(SHEET_CSV_URL)
            if status == "Clock OUT":
                # Match Name and Date where Clock OUT is empty
                match = df[(df['Date'] == dt) & (df['Employee'] == name) & (df['Clock OUT'].isna())]
                if not match.empty:
                    # Determine correct column name from your sheet
                    col_in = 'Clock IN' if 'Clock IN' in df.columns else 'Clock In'
                    t_in = pd.to_datetime(match.iloc[-1][col_in])
                    t_out = pd.to_datetime(tm)
                    hrs = (t_out - t_in).total_seconds() / 3600
                    if hrs > 5: hrs -= 1 # Auto-lunch
                    params["Hours"] = round(hrs, 2)
                    params["Pay"] = f"₱{round(hrs * HOURLY_RATE, 2)}"

            # Submit Data First (Priority)
            res = requests.get(DEPLOYMENT_URL, params=params, timeout=15)
            
            if "SYNC_OK" in res.text:
                st.success(f"✅ {status} Synced!")
                # Submit Photo Second (To avoid postData error crashing the log)
                img_b64 = base64.b64encode(img.getvalue()).decode()
                requests.post(DEPLOYMENT_URL, json={"image": img_b64, "filename": f"{dt}_{name}.jpg"}, timeout=10)
                st.balloons()
            else:
                st.warning("Logged, but check sheet for pay calculation.")

        except Exception as e:
            st.error("Connection Error. Please check your Web App URL.")

# --- 3. MANAGER DASHBOARD (Locked) ---
# This section ONLY shows if admin_mode is True and password is correct
if admin_mode and admin_pw == "Hmaxine":
    st.divider()
    st.subheader("🛡️ Manager Dashboard")
    
    if st.button("📧 Send Weekly Payroll Report"):
        with st.spinner("Sending..."):
            r = requests.get(DEPLOYMENT_URL, params={"Action": "SendReport"})
            st.success("Report Sent!") if "REPORT_SENT" in r.text else st.error("Failed.")

    try:
        df_db = pd.read_csv(SHEET_CSV_URL)
        st.dataframe(df_db)
    except:
        st.info("Awaiting data...")
