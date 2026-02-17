import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. SETUP
st.set_page_config(page_title="Printquency", page_icon="⏰")
FILE_NAME = "Payroll_Master_Tracker.csv"

st.header("🖨️ Printquency Time Clock", divider="blue")

# 2. SELECTION
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Employee:", names)
status = st.radio("Action:", ["Clock IN", "Clock OUT"], horizontal=True)

if name != "SELECT NAME":
    img = st.camera_input("Verify with Selfie")
    
    if img:
        now = datetime.now()
        new_row = {"Date": now.strftime("%Y-%m-%d"), "Time": now.strftime("%H:%M:%S"), "Employee": name, "Status": status}
        
        # Save Logic
        df = pd.DataFrame([new_row])
        if os.path.exists(FILE_NAME):
            df = pd.concat([pd.read_csv(FILE_NAME), df], ignore_index=True)
        df.to_csv(FILE_NAME, index=False)
        
        st.success(f"✅ {status} Logged for {name}!")
        st.balloons()

# 3. ADMIN
st.divider()
with st.expander("🛡️ Admin Panel"):
    pw = st.text_input("Password", type="password")
    if pw == "Hmaxine":
        if os.path.exists(FILE_NAME):
            data = pd.read_csv(FILE_NAME)
            st.write("### Today's Logs")
            st.dataframe(data)
            
            # Simple Download
            with open(FILE_NAME, "rb") as f:
                st.download_button("📥 Download Records", f, file_name="payroll.csv")
            
            # Reset Button
            if st.button("🗑️ Reset File"):
                os.remove(FILE_NAME)
                st.rerun()
        else:
            st.info("No records yet.")
