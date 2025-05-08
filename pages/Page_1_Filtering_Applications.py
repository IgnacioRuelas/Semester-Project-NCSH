import pandas as pd
import streamlit as st
df = pd.read_csv('NHS_Data.csv')
approved_df = df[df["Request Status"] == "Approved"]

def clean_signed_status(val):
    if pd.isna(val) or str(val).strip().lower() in ["", "N/A"]:
      return "Missing"
    elif str(val).strip().lower() == "yes":
      return "Yes"
    elif str(val).strip().lower() == "YES":
      return "Yes"
    elif str(val).strip().lower() == "no":
      return "No"
    else:
      return "Missing"

approved_df["Application Signed Cleaned"] = approved_df["Application Signed?"].apply(clean_signed_status)

summary = approved_df["Application Signed Cleaned"].value_counts(dropna=False).reset_index()
summary.columns = ["Application Signed?", "Count"]
summary["Percentage"] = (summary["Count"] / summary["Count"].sum() * 100).round(2)

display_df = approved_df[["Patient ID#", "Application Signed Cleaned"]].rename(
    columns={"Application Signed Cleaned": "Application Signed?"}
).reset_index(drop=True)

st.title("Approved Applications Page")
st.subheader("Summary of Application Signed Status")
st.table(summary, hide_index=True)

st.subheader("Filter by Application Signed Status")
status_filter = st.selectbox("Select a status",["All", "Yes", "No", "Missing"])

if status_filter != "All":
  filtered_df = display_df[display_df["Application Signed?"] == status_filter]
else:
  filtered_df = display_df
st.subheader("Filtered Approved Applications")
st.dataframe(filtered_df, hide_index=True)
