import streamlit as st
from datetime import datetime
import pandas as pd
import os

st.set_page_config(page_title="Shop Time-Clock", page_icon="⏰")

st.title("🇵🇭 Shop Time-Clock")

# 1. Employee Selection
employee_list = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Your Name:", employee_list)

# 2. Status Selection (IN or OUT)
status = st.radio("What are you doing?", ["Clock IN", "Clock OUT"], horizontal=True)

if name != "SELECT NAME":
    st.info(f"Hello {name}, taking photo for {status}...")
    img = st.camera_input("Smile for the camera!")
    
    if img:
        now = datetime.now()
        new_data = {
            "Date": now.strftime("%Y-%m-%d"),
            "Time": now.strftime("%H:%M:%S"),
            "Employee": name,
            "Status": status # Now records if they are In or Out
        }
        
        file = "Payroll_Master_Tracker.csv"
        df_new = pd.DataFrame([new_data])
        
        if os.path.exists(file):
            df_old = pd.read_csv(file)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_final = df_new
            
        df_final.to_csv(file, index=False)
        st.success(f"✅ {status} recorded for {name} at {new_data['Time']}")
        st.balloons()

# --- ADMIN SECTION ---
st.divider()
if st.checkbox("Admin: Show Records"):
    if os.path.exists("Payroll_Master_Tracker.csv"):
        df_view = pd.read_csv("Payroll_Master_Tracker.csv")
        st.dataframe(df_view)
        with open("Payroll_Master_Tracker.csv", "rb") as f:
            st.download_button("📥 Download Records", f, file_name="payroll_logs.csv")
