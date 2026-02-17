import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. SETUP & LINKS
st.set_page_config(page_title="Printquency", page_icon="⏰")
HOURLY_RATE = 80.00

# PASTE YOUR WEB APP URL HERE (Ending in /exec)
DEPLOYMENT_URL = "https://script.google.com/macros/s/AKfycbyBHAwzfzr6nm5uEInSXpGRmZjQIL1XxiSJC-saM3ngHmIqsvp4nAIQkxJSXCVDvYwiUg/exec"

# YOUR SPECIFIC SHEET LINK FOR READING DATA
SHEET_ID = "1JAUdxkqV3CmCUZ8EGyhshI6AVhU_rJ1T9N7FE5-JmZM"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.header("🖨️ Printquency Time Clock", divider="blue")

# 2. EMPLOYEE INTERFACE
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Employee Name:", names)
status = st.radio("Action:", ["Clock IN", "Clock OUT"], horizontal=True)

if name != "SELECT NAME":
    img = st.camera_input("Verify with Selfie")
    
    if img:
        now = datetime.now()
        data = {
            "Date": now.strftime("%Y-%m-%d"),
            "Time": now.strftime("%H:%M:%S"),
            "Employee": name,
            "Status": status
        }
        
        # AUTO-SEND TO GOOGLE SHEETS
        try:
            response = requests.get(DEPLOYMENT_URL, params=data)
            if response.status_code == 200:
                st.success(f"✅ {status} Logged to Google Sheets for {name}!")
                st.balloons()
            else:
                st.error("Sheet link failed. Check Deployment URL.")
        except Exception as e:
            st.error("Connection Error. Is your internet active?")

# 3. ADMIN PANEL (Password: Hmaxine)
st.divider()
with st.expander("🛡️ Admin Panel"):
    pw = st.text_input("Password", type="password")
    if pw == "Hmaxine":
        try:
            df = pd.read_csv(SHEET_CSV_URL)
            st.write(f"### Pay Summary (₱{HOURLY_RATE}/hr)")
            
            summary = []
            for (date, emp), group in df.groupby(['Date', 'Employee']):
                ins = group[group['Status'].str.contains('IN', case=False, na=False)]
                outs = group[group['Status'].str.contains('OUT', case=False, na=False)]
                
                if not ins.empty and not outs.empty:
                    t1 = pd.to_datetime(ins.iloc[0]['Time'], format='%H:%M:%S')
                    t2 = pd.to_datetime(outs.iloc[-1]['Time'], format='%H:%M:%S')
                    hrs = (t2 - t1).seconds / 3600
                    summary.append({
                        "Date": date, "Name": emp, "Hours": round(hrs, 2), 
                        "Pay": f"₱{round(hrs * HOURLY_RATE, 2)}"
                    })
            
            if summary:
                st.table(pd.DataFrame(summary))
            st.dataframe(df)
            st.link_button("📂 Open Google Sheet", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
        except:
            st.info("Check if your Sheet is shared as 'Anyone with the link can view'.")
