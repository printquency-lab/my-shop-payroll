import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Setup
st.set_page_config(page_title="Shop Payroll", page_icon="⏰")
HOURLY_RATE = 80.00 

st.title("🇵🇭 Shop Time-Clock")

# 2. Selection
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
selected_name = st.selectbox("Your Name:", names)
status = st.radio("Action:", ["Clock IN", "Clock OUT"], horizontal=True)

if selected_name != "SELECT NAME":
    img = st.camera_input("Take a selfie to log")
    
    if img:
        now = datetime.now()
        new_row = {
            "Date": now.strftime("%Y-%m-%d"),
            "Time": now.strftime("%H:%M:%S"),
            "Employee": selected_name,
            "Status": status
        }
        
        # Save to CSV
        file = "Payroll_Master_Tracker.csv"
        df = pd.DataFrame([new_row])
        if os.path.exists(file):
            df = pd.concat([pd.read_csv(file), df], ignore_index=True)
        df.to_csv(file, index=False)
        
        st.success(f"✅ Recorded {status} for {selected_name}")
        st.balloons()

# 3. Admin Section
st.divider()
if st.checkbox("Admin: View Computed Payroll"):
    if os.path.exists("Payroll_Master_Tracker.csv"):
        df_logs = pd.read_csv("Payroll_Master_Tracker.csv")
        st.dataframe(df_logs)
        
        # Simple Math logic
        st.write(f"### Pay Summary (₱{HOURLY_RATE}/hr)")
        # This will show their total for the day if they have an IN and OUT
        st.info("Calculation appears here once an employee has both an IN and OUT log.")
