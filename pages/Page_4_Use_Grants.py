#Page four: how many patients did not use their full grant amount in a given application year. What are the average amounts given by assistance type?

import streamlit as st
import pandas as pd
import plotly.express as px

st.title("Effective Use of Financial Support and Type of Assistance")

#Using the shared CSV file
df = pd.read_csv('NHS_Data.csv')

# 1. Filter to approved
df_approved = df[df["Request Status"].str.strip().str.lower() == "approved"].copy()

# 2. Drop rows with missing critical data
# Changed "Remaining balance" to the actual column name "Remaining Balance"
usage_df = df_approved.dropna(subset=["App Year", "Remaining Balance"]).copy()

# Convert columns to numeric just in case
usage_df["App Year"] = pd.to_numeric(usage_df["App Year"], errors="coerce")
usage_df["Remaining Balance"] = pd.to_numeric(usage_df["Remaining Balance"], errors="coerce")

# Focus on App Year 1–6
usage_df = usage_df[(usage_df["App Year"] >= 1) & (usage_df["App Year"] <= 6)]

# Create usage status
def grant_status(balance):
    if balance == 0:
        return "Fully Used"
    elif balance < 0:
        return "Overused"
    else:
        return "Remaining"

# Changed "Remaining balance" to the actual column name "Remaining Balance"
usage_df["Grant Usage Status"] = usage_df["Remaining Balance"].apply(grant_status)

# Group by App Year and Usage Status
summary = usage_df.groupby(["App Year", "Grant Usage Status"]).size().unstack(fill_value=0)

# Add total and percentage
summary["Total"] = summary.sum(axis=1)
summary["Fully Used %"] = (summary.get("Fully Used", 0) / summary["Total"] * 100).round(1)
summary["Overused %"] = (summary.get("Overused", 0) / summary["Total"] * 100).round(1)
summary["Remaining %"] = (summary.get("Remaining", 0) / summary["Total"] * 100).round(1)

summary["Fully Used %"] = summary["Fully Used %"].map(lambda x: f"{x:.1f}%")
summary["Overused %"] = summary["Overused %"].map(lambda x: f"{x:.1f}%")
summary["Remaining %"] = summary["Remaining %"].map(lambda x: f"{x:.1f}%")

# Display
st.subheader("Grant Usage Summary by Application Year")
st.dataframe(summary)

# Total usage distribution (across all App Years)
overall_counts = usage_df["Grant Usage Status"].value_counts().reset_index()
overall_counts.columns = ["Grant Usage", "Count"]

# Add percentage column for reference
overall_counts["Percentage"] = (overall_counts["Count"] / overall_counts["Count"].sum() * 100).round(1)

# Pie chart
fig = px.pie(
    overall_counts,
    names="Grant Usage",
    values="Count",
    title="Overall Grant Usage Distribution (Approved Applications)",
    color_discrete_sequence=px.colors.qualitative.Set3,
    hole=0.4  # donut chart style
)

st.plotly_chart(fig)

#identifying average amount by type of assistance

st.subheader("Average Grant Amount by Assistance Type")

# --- Clean "Amount" and "Type of Assistance (CLASS)" ---
df_approved["Amount"] = pd.to_numeric(df_approved["Amount"], errors="coerce")

def clean_assistance_type(value):
    if pd.isna(value):
        return "Missing"
    val = value.strip().lower()
    if "housing" in val:
        return "Housing"
    return val.title()

df_approved["Assistance Type"] = df_approved["Type of Assistance (CLASS)"].apply(clean_assistance_type)

# --- Group by Assistance Type and calculate average ---
avg_amounts = (
    df_approved.groupby("Assistance Type")["Amount"]
    .mean()
    .round(2)
    .sort_values(ascending=False)
    .reset_index()
)

# --- Format dollar amounts for display in chart labels ---
avg_amounts["Amount Label"] = avg_amounts["Amount"].map(lambda x: f"${x:,.2f}")

# --- Plot using Plotly for horizontal, sorted bar chart ---
fig = px.bar(
    avg_amounts,
    x="Amount",
    y="Assistance Type",
    orientation="h",
    text="Amount Label",
    title="Average Grant Amount by Assistance Type (Approved Only)",
    labels={"Amount": "Avg Amount ($)", "Assistance Type": "Assistance Type"},
)

fig.update_traces(textposition="outside")
fig.update_layout(
    yaxis=dict(categoryorder='total ascending'),  # largest at top
    xaxis_tickprefix="$",
    xaxis_title="Average Amount ($)",
    yaxis_title=""
)
# Show table (optional)
st.dataframe(avg_amounts[["Assistance Type", "Amount Label"]].rename(columns={"Amount Label": "Average Amount ($)"}))

# --- Show chart in Streamlit ---
st.plotly_chart(fig, use_container_width=True)
