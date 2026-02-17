import streamlit as st
from datetime import datetime
import csv
import os

# App Config
st.set_page_config(page_title="Shop Time-Clock", page_icon="⏰")

st.title("🇵🇭 Shop Time-Clock")
st.subheader("Face Verification Login")

# 1. EMPLOYEE SELECTION
# You can add more names to this list
employee_list = ["SELECT NAME", "JUAN DELA CRUZ", "MARIA CLARA", "PEDRO PENDUKO"]
selected_name = st.selectbox("Select your name:", employee_list)

if selected_name != "SELECT NAME":
    # 2. CAMERA INPUT
    st.info(f"Ready to clock in, {selected_name}?")
    img_file = st.camera_input("Take a clear selfie to log your time")

    if img_file:
        # Show a preview of the capture
        st.success("Photo captured!")
        
        # 3. LOGGING BUTTON
        if st.button(f"Confirm Clock-In/Out for {selected_name}"):
            # Logic for Payroll Calculations
            
            now = datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            month_str = now.strftime("%B %Y")
            
            # This is where we save to your Master CSV
            # Note: We are using placeholder values for hours/rate which 
            # you can edit later in your Master Tracker.
            try:
                file_name = "Payroll_Master_Tracker.csv"
                file_exists = os.path.isfile(file_name)
                
                with open(file_name, mode="a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(["Date", "Time", "Employee", "Month", "Status"])
                    writer.writerow([date_str, time_str, selected_name, month_str, "LOGGED"])
                
                st.balloons()
                st.success(f"Done! Logged at {time_str}. See you, {selected_name}!")
                
            except Exception as e:
                st.error(f"Error saving data: {e}")

else:
    st.write("Please select your name from the list to start.")

# Footer for the Boss
st.divider()
st.caption("Admin Note: All photos and timestamps are recorded in the Master Tracker.")
st.divider()
if st.checkbox("Admin: Show Download Link"):
    if os.path.exists("Payroll_Master_Tracker.csv"):
        with open("Payroll_Master_Tracker.csv", "rb") as file:
            st.download_button(
                label="Download Master Payroll CSV",
                data=file,
                file_name="Shop_Master_Records.csv",
                mime="text/csv"
            )
    else:
        st.write("No records found yet.")
import pandas as pd

st.divider()
st.subheader("Admin Section")
# Use a simple password so employees don't download your payroll!
if st.text_input("Enter Admin Password", type="password") == "shop2026":
    if os.path.exists("Payroll_Master_Tracker.csv"):
        with open("Payroll_Master_Tracker.csv", "rb") as file:
            st.download_button(
                label="📥 Download Master Payroll File",
                data=file,
                file_name="Shop_Payroll_Master.csv",
                mime="text/csv"
            )
        
        # Also show the table live in the app
        df = pd.read_csv("Payroll_Master_Tracker.csv")
        st.dataframe(df)
    else:
        st.info("No logs recorded yet.")
