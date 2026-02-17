import streamlit as st  # This line prevents the NameError
import pandas as pd
import os
from datetime import datetime

# 1. SETUP & THEME
st.set_page_config(page_title="Printquency Payroll", page_icon="⏰")
HOURLY_RATE = 80.00 

# Your new shop header
st.header("🖨️ Printquency Time Clock", divider="blue")

# 2. EMPLOYEE SELECTION
names = ["SELECT NAME", "Adam Lozada", "Mark Alejandro"]
selected_name = st.selectbox("Select Employee:", names)

# Mobile-friendly layout for buttons
col1, col2 = st.columns(2)
with col1:
    status = st.radio("Action:", ["Clock IN", "Clock OUT"])

if selected_name != "SELECT NAME":
    st.info(f"Logging {status} for {selected_name}")
    img = st.camera_input("Take a selfie to verify")
    
    if img:
        now = datetime.now()
        new_row = {
            "Date": now.strftime("%Y-%m-%d"),
            "Time": now.strftime("%H:%M:%S"),
            "Employee": selected_name,
            "Status": status
        }
        
        # Save to CSV (local cloud memory)
        file = "Payroll_Master_Tracker.csv"
        df = pd.DataFrame([new_row])
        if os.path.exists(file):
            df = pd.concat([pd.read_csv(file), df], ignore_index=True)
        df.to_csv(file, index=False)
        
        st.success(f"✅ Recorded! See you, {selected_name.split()[0]}!")
        st.balloons()

# 3. ADMIN SECTION
st.divider()
with st.expander("🛡️ Admin: View Records & Computation"):
    password = st.text_input("Enter Admin Password", type="password")
    if password == "printquency123": 
        if os.path.exists("Payroll_Master_Tracker.csv"):
            df_logs = pd.read_csv("Payroll_Master_Tracker.csv")
            
            st.write(f"### Pay Summary (₱{HOURLY_RATE}/hr)")
            
            # Simple Math logic for the day
            summary_data = []
            for (date, emp), group in df_logs.groupby(['Date', 'Employee']):
                ins = group[group['Status'] == 'Clock IN']
                outs = group[group['Status'] == 'Clock OUT']
                
                if not ins.empty and not outs.empty:
                    t1 = pd.to_datetime(ins.iloc[0]['Time'], format='%H:%M:%S')
                    t2 = pd.to_datetime(outs.iloc[-1]['Time'], format='%H:%M:%S')
                    hours = (t2 - t1).seconds / 3600
                    total = hours * HOURLY_RATE
                    summary_data.append({
                        "Date": date,
                        "Employee": emp,
                        "Hours": round(hours, 2),
                        "Total Pay": f"₱{round(total, 2)}"
                    })
            
            if summary_data:
                st.table(pd.DataFrame(summary_data))
            else:
                st.info("Need both an IN and OUT log for the same day to calculate pay.")
                
            st.write("### All Raw Logs")
            st.dataframe(df_logs)
            
            with open("Payroll_Master_Tracker.csv", "rb") as f:
                st.download_button("📥 Download Master File", f, file_name="Printquency_Logs.csv")
        else:
            st.info("No records found yet.")
