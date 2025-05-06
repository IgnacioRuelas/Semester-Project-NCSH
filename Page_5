st.title("Nebraska Cancer Specialists Hope Foundation: High-level summary")


df = pd.read_csv('/content/NHS_Data.csv')  

# ---------- Clean Column Names ----------
df.columns = df.columns.str.strip()

# ---------- Clean 'Type of Assistance (CLASS)' ----------
df['Type of Assistance (CLASS)'] = (
    df['Type of Assistance (CLASS)']
    .astype(str)
    .str.strip()
    .str.title()
    .replace({'None': 'Missing', 'Nan': 'Missing', '': 'Missing'})
)

# ---------- Ensure Amount is Numeric ----------
df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')

# ---------- Mission Statement ----------
st.subheader("Mission")
st.markdown("""
The NCS HOPE Foundation seeks to improve the lives of individuals and families in the community who are impacted by cancer treatment.
The foundation provides financial assistance, supportive services, and other resources to oncology and hematology patients, families, and caregivers receiving care in Nebraska.
""")

# ---------- Request Status Summary ----------
st.subheader("Request Summary")
status_counts = df['Request Status'].value_counts()
status_percent = (status_counts / len(df)).apply(lambda x: f"{x:.2%}")
summary_df = pd.DataFrame({
    "Count": status_counts,
    "Percentage": status_percent
})
st.dataframe(summary_df)

# ---------- Pie Chart of Request Status ----------
st.subheader("Request Status Distribution (Pie Chart)")
status_counts_df = df['Request Status'].value_counts().reset_index()
status_counts_df.columns = ['Request Status', 'Count']
status_counts_df['Percentage'] = (status_counts_df['Count'] / len(df)).apply(lambda x: f"{x:.2%}")

fig = px.pie(
    status_counts_df,
    names='Request Status',
    values='Count',
    title='Request Status Distribution',
    hole=0.4,
)
fig.update_traces(textinfo='label+percent+value',
                  hovertemplate="%{label}<br>Count: %{value}<br>Percent: %{percent}")
st.plotly_chart(fig)

# ---------- Approved Requests ----------
approved_df = df[df['Request Status'] == 'Approved']

st.subheader("Approved Financial Support Summary")
if not approved_df.empty:
    total_approved_amount = approved_df['Amount'].sum()
    st.metric(label="Total Financial Support Approved", value=f"${total_approved_amount:,.2f}")

    # Distribution by Type of Assistance (CLASS)
    dist_by_class = (
        approved_df.groupby("Type of Assistance (CLASS)")["Amount"]
        .agg(['sum', 'count'])
        .rename(columns={'sum': 'Total Amount', 'count': 'Number of Requests'})
    )
    dist_by_class["Percentage of Total Amount"] = (
        dist_by_class["Total Amount"] / total_approved_amount
    ).apply(lambda x: f"{x:.2%}")
    dist_by_class["Total Amount"] = dist_by_class["Total Amount"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(dist_by_class)

    # Patient Count and Percentage by Assistance Type
    st.subheader("Patient Distribution by Type of Assistance")
    patient_counts = approved_df['Type of Assistance (CLASS)'].value_counts()
    patient_percent = (patient_counts / len(approved_df)).apply(lambda x: f"{x:.2%}")
    patient_summary = pd.DataFrame({
        "Count of Patients": patient_counts,
        "Percentage": patient_percent
    })
    st.dataframe(patient_summary)
else:
    st.info("No approved requests to display.")
