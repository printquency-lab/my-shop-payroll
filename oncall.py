import streamlit as st
from datetime import datetime
import pandas as pd
import os

st.set_page_config(page_title="Shop Time-Clock", page_icon="⏰")

st.title("🇵🇭 Shop Time-Clock")

# 1. Updated Employee Selection
employee_list = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
name = st.selectbox("Your Name:", employee_list)

if name != "SELECT NAME":
    # 2. Camera Input
    st.info(f"Hello {name}, please take a selfie to Clock-In/Out.")
    img = st.camera_input("Smile for the camera!")
    
    if img:
        # 3. Data Processing
        now = datetime.now()
        new_data = {
            "Date": now.strftime("%Y-%m-%d"),
            "Time": now.strftime("%H:%M:%S"),
            "Employee": name,
            "Status": "LOGGED"
        }
        
        # 4. Save to CSV Logic
        file = "Payroll_Master_Tracker.csv"
        df_new = pd.DataFrame([new_data])
        
        if os.path.exists(file):
            df_old = pd.read_csv(file)
            df_final = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df_final = df_new
            
        df_final.to_csv(file, index=False)
        st.success(f"✅ Logged successfully for {name} at {new_data['Time']}")
        st.balloons()

# --- ADMIN SECTION (Hidden by default) ---
st.divider()
admin_check = st.checkbox("Admin: Show Records")

if admin_check:
    st.subheader("📊 Manager's Master View")
    if os.path.exists("Payroll_Master_Tracker.csv"):
        df_view = pd.read_csv("Payroll_Master_Tracker.csv")
        st.dataframe(df_view) # Shows all logs
        
        # Download Button
        with open("Payroll_Master_Tracker.csv", "rb") as f:
            st.download_button("📥 Download All Records (CSV)", f, file_name="payroll_logs.csv")
    else:
        st.info("No logs recorded yet. Try a test entry!")
