import streamlit as st
import pandas as pd
from datetime import datetime

# 1. SETUP & GSHEET CONNECTION
st.set_page_config(page_title="Printquency", page_icon="⏰")
HOURLY_RATE = 80.00

# Your specific Google Sheet ID
SHEET_ID = "1JAUdxkqV3CmCUZ8EGyhshI6AVhU_rJ1T9N7FE5-JmZM"
# This link allows the app to READ your data live
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

st.header("🖨️ Printquency Time Clock", divider="blue")

# 2. EMPLOYEE INTERFACE
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Employee Name:", names)
status = st.radio("Action:", ["Clock IN", "Clock OUT"], horizontal=True)

if name != "SELECT NAME":
    img = st.camera_input("Verify with Selfie")
    
    if img:
        st.success(f"✅ Selfie captured! Data is ready for the sheet.")
        st.info("Note: Manual entry in the Google Sheet is currently required to see the math below.")
        st.balloons()

# 3. ADMIN PANEL (Password: Hmaxine)
st.divider()
with st.expander("🛡️ Admin Panel"):
    pw = st.text_input("Password", type="password")
    if pw == "Hmaxine":
        try:
            # Pull data live from your specific GSheet
            df = pd.read_csv(SHEET_CSV_URL)
            
            st.write("### Live Payroll Summary")
            
            # MATH LOGIC: Finds matching IN and OUT rows for the same date/person
            summary = []
            if not df.empty:
                for (date, emp), group in df.groupby(['Date', 'Employee']):
                    ins = group[group['Status'].str.contains('IN', case=False, na=False)]
                    outs = group[group['Status'].str.contains('OUT', case=False, na=False)]
                    
                    if not ins.empty and not outs.empty:
                        t1 = pd.to_datetime(ins.iloc[0]['Time'], format='%H:%M:%S')
                        t2 = pd.to_datetime(outs.iloc[-1]['Time'], format='%H:%M:%S')
                        hrs = (t2 - t1).seconds / 3600
                        summary.append({
                            "Date": date, 
                            "Name": emp, 
                            "Hours": round(hrs, 2),
                            "Pay": f"₱{round(hrs * HOURLY_RATE, 2)}"
                        })
            
            if summary:
                st.table(pd.DataFrame(summary))
            else:
                st.info("No complete pairs (IN/OUT) found in the sheet yet.")
            
            st.write("### All Sheet Records")
            st.dataframe(df)
            
            # Direct link to your sheet for easy editing
            st.link_button("📂 Open Original Google Sheet", f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit")
            
        except Exception as e:
            st.error("Cannot read the Google Sheet. Please ensure it is shared as 'Anyone with the link can view'.")
