import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

# Your Specific Shop Location
SHOP_LAT = 14.687029522810302
SHOP_LON = 120.94033084321396

def generate_cutoff_report():
    file_name = "Payroll_Master_Tracker.csv"
    if not os.path.exists(file_name):
        return "No data found."

    # Load the data
    df = pd.read_csv(file_name)
    
    # Determine the current Cut-off Period
    today = datetime.now()
    if today.day <= 15:
        period = f"{today.strftime('%B')} 1-15"
    else:
        period = f"{today.strftime('%B')} 16-30/31"

    # Create PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Header
    pdf.cell(190, 10, "OFFICIAL PAYROLL SUMMARY REPORT", ln=True, align='C')
    pdf.set_font("Arial", '', 12)
    pdf.cell(190, 10, f"Location: {SHOP_LAT}, {SHOP_LON}", ln=True, align='C')
    pdf.cell(190, 10, f"Cut-off Period: {period}", ln=True, align='C')
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "Employee", 1)
    pdf.cell(40, 10, "Total Hours", 1)
    pdf.cell(40, 10, "Total Paid (PHP)", 1)
    pdf.ln()

    # Data Rows
    pdf.set_font("Arial", '', 10)
    grand_total = 0
    
    # Group by Employee to get totals for the period
    summary = df.groupby('Employee')['TotalPaid'].sum().reset_index()
    hours_sum = df.groupby('Employee')['Hours'].sum().reset_index()

    for i in range(len(summary)):
        name = summary.iloc[i]['Employee']
        paid = summary.iloc[i]['TotalPaid']
        hours = hours_sum.iloc[i]['Hours']
        grand_total += paid
        
        pdf.cell(60, 10, name, 1)
        pdf.cell(40, 10, f"{hours:.2f}", 1)
        pdf.cell(40, 10, f"P {paid:,.2f}", 1)
        pdf.ln()

    # Final Total
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, "GRAND TOTAL PAYOUT", 1)
    pdf.cell(40, 10, f"P {grand_total:,.2f}", 1)

    report_name = f"Payroll_Report_{period.replace(' ', '_')}.pdf"
    pdf.output(report_name)
    return f"Report Generated: {report_name}"

# To run it automatically:
if __name__ == "__main__":
    print(generate_cutoff_report())
