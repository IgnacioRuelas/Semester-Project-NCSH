#Using the shared CSV file
df = pd.read_csv('/content/NHS_Data.csv')

approved_df = df[df["Request Status"] == "Approved"]

#CLEANING

approved_df["Payment Submitted?"] = approved_df["Payment Submitted?"].replace(
    {"Yes": None, "No": None}
)

# Ensure columns are numeric before converting to datetime
approved_df["Grant Req Date"] = pd.to_numeric(approved_df["Grant Req Date"], errors="coerce")
approved_df["Payment Submitted?"] = pd.to_numeric(approved_df["Payment Submitted?"], errors="coerce")

#convert to datetime

origin_date = pd.to_datetime("1899-12-30")
approved_df["Grant Req Date"] = origin_date + pd.to_timedelta(approved_df["Grant Req Date"], unit="D")
approved_df["Payment Submitted?"] = origin_date + pd.to_timedelta(approved_df["Payment Submitted?"], unit="D")


#Calculating time to make the support effective

approved_df["Days to Support"] = (approved_df["Payment Submitted?"] - approved_df["Grant Req Date"]).dt.days
# Convert to absolute value
approved_df["Days to Support"] = approved_df["Days to Support"].abs()


#Defining bins with a '0' group
bins = [-0.1, 0, 7, 14, 30, 60, 90, 180, 365, float('inf')]
labels = ['0', '1-7', '8-14', '15-30', '31-60', '61-90', '91-180', '181-365', '365+']

approved_df['Support Bin'] = pd.cut(
    approved_df["Days to Support"],
    bins=bins,
    labels=labels,
    right=True  # includes right edge in the bin
)

#Grouping by bins and calculate counts and percentages
bin_counts = approved_df['Support Bin'].value_counts(sort=False)
bin_percentages = (bin_counts / bin_counts.sum() * 100).round(2)

#Creating summary table
summary_table = pd.DataFrame({
    'Count': bin_counts,
    'Percentage (%)': bin_percentages
}).reset_index().rename(columns={'index': 'Days to Support Range'})

summary_table = summary_table.style.format({"Percentage (%)": "{:.1f}%"})

#Displaying summary table in Streamlit
st.title("How many days does providing support take?")
st.subheader("Days to Spend Support: Distribution by Bin")
st.dataframe(summary_table)

# Displaying chart
# Rebuild or access unformatted summary_table if needed
chart_data = pd.DataFrame({
    'Days to Support Range': labels,
    'Count': bin_counts.values,
    'Percentage': bin_percentages.values
})

# Create horizontal bar chart
fig = px.bar(
    chart_data,
    x='Count',
    y='Days to Support Range',
    orientation='h',
    text=chart_data['Percentage'].map(lambda x: f"{x:.1f}%"),
    labels={'Count': 'Number of Cases', 'Days to Support Range': 'Days to Support'},
    title='Distribution of Days to Support (Horizontal Bar)'
)

fig.update_traces(textposition='outside')
fig.update_layout(
    yaxis=dict(categoryorder='total ascending'),
    xaxis_title='Count',
    yaxis_title='Days to Support Range',
    height=500
)

#Displaying chart in Streamlit
st.subheader("Days to Spend Support: Distribution by Bin")
st.plotly_chart(fig)


#Displaying summary statistics in streamlit. Note: The distribution of data in this table corresponds with the counts in each bin
st.subheader("Summary Statistics for 'Days to Support'")
st.dataframe(approved_df["Days to Support"].describe().to_frame())
