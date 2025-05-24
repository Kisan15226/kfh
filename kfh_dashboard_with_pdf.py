
import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import tempfile

# Load data
df = pd.read_csv("STI Ravi  - Sheet16.csv")

st.title("KFH Attendance and Product Dashboard")

# Sidebar filters
kfh_filter = st.sidebar.multiselect("Select KFHName:", options=df['KFHName'].unique(), default=df['KFHName'].unique())
rack_filter = st.sidebar.multiselect("Select RackName:", options=df['RackName'].unique(), default=df['RackName'].unique())
section_filter = st.sidebar.multiselect("Select SectionName:", options=df['SectionName'].unique(), default=df['SectionName'].unique())

# Apply filters
filtered_df = df[
    df['KFHName'].isin(kfh_filter) &
    df['RackName'].isin(rack_filter) &
    df['SectionName'].isin(section_filter)
]

st.subheader("Filtered Results")
st.dataframe(filtered_df)

# Download button for filtered data
st.download_button(
    label="Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False),
    file_name='filtered_kfh_data.csv',
    mime='text/csv'
)

# Summary stats
total_entries = filtered_df.shape[0]
unique_products = filtered_df['ProductName'].nunique()
avg_priority = round(filtered_df['PickingPriority'].mean(), 2)

st.subheader("Summary")
st.write("Total Entries:", total_entries)
st.write("Unique Products:", unique_products)
st.write("Average Picking Priority:", avg_priority)

# Charts
st.subheader("Visualizations")

product_count = filtered_df['KFHName'].value_counts().reset_index()
product_count.columns = ['KFHName', 'Count']
fig1 = px.bar(product_count, x='KFHName', y='Count', title='Product Entries per KFHName')
st.plotly_chart(fig1)

priority_avg = filtered_df.groupby('SectionName')['PickingPriority'].mean().reset_index()
fig2 = px.bar(priority_avg, x='SectionName', y='PickingPriority', title='Average Picking Priority by Section')
st.plotly_chart(fig2)

top_products = filtered_df['ProductName'].value_counts().nlargest(10).reset_index()
top_products.columns = ['ProductName', 'Count']
fig3 = px.bar(top_products, x='ProductName', y='Count', title='Top 10 Products by Frequency')
st.plotly_chart(fig3)

# Export to PDF
st.subheader("Export Report to PDF")

def generate_pdf(data_summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="KFH Attendance and Product Dashboard Report", ln=True, align='C')
    pdf.ln(10)

    for key, value in data_summary.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_pdf.name)
    return temp_pdf

if st.button("Generate PDF Summary"):
    summary_data = {
        "Total Entries": total_entries,
        "Unique Products": unique_products,
        "Average Picking Priority": avg_priority
    }
    pdf_file = generate_pdf(summary_data)
    with open(pdf_file.name, "rb") as f:
        st.download_button("Download PDF", data=f, file_name="kfh_report.pdf", mime="application/pdf")
