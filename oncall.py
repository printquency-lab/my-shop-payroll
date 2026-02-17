# --- ADD THIS TO YOUR ADMIN SECTION ---
if st.checkbox("Admin: View Computed Payroll"):
    if os.path.exists("Payroll_Master_Tracker.csv"):
        df = pd.read_csv("Payroll_Master_Tracker.csv")
        
        # Convert Time to actual numbers for math
        df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')
        
        # Group by Date and Employee
        summary = []
        for (date, emp), group in df.groupby(['Date', 'Employee']):
            ins = group[group['Status'] == 'Clock IN']
            outs = group[group['Status'] == 'Clock OUT']
            
            if not ins.empty and not outs.empty:
                start = ins['Time'].iloc[0]
                end = outs['Time'].iloc[-1]
                duration = (end - start).seconds / 3600
                
                # Apply your Shop Rate (₱61.38 from your payslip)
                rate = 61.38
                pay = duration * rate
                
                summary.append({
                    "Date": date,
                    "Employee": emp,
                    "Total Hours": round(duration, 2),
                    "Pay (PHP)": round(pay, 2)
                })
        
        if summary:
            st.table(pd.DataFrame(summary))
        else:
            st.info("Need both an 'IN' and an 'OUT' log for the same day to compute.")
