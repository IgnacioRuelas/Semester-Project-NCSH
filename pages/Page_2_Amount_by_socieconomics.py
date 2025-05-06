#Using the shared CSV file
df = pd.read_csv('/content/NHS_Data.csv')

#DATA CLEAINING

#Fitering and considering only those whose request status is approved

approved_df = df[df["Request Status"] == "Approved"]

# Convert 'Amount' to string and replace special characters
approved_df["Amount"] = approved_df["Amount"].astype(str).str.replace(r"[$,]", "", regex=True)
approved_df["Amount"] = pd.to_numeric(approved_df["Amount"], errors="coerce")


#Fitering so the financial information breaksdown into locations

approved_df["Pt City"] = approved_df["Pt City"].astype(str).str.title()

#Fitering so the financial information breaksdown according to gender

approved_df["Gender"] = approved_df["Gender"].fillna("Missing").astype(str)
approved_df["Gender"] = approved_df["Gender"].str.title()
approved_df["Gender"] = approved_df["Gender"].where(approved_df["Gender"].isin(["Male", "Female"]), "Missing")

#Fitering so the financial information breaksdown according to Insurance

approved_df["Insurance Type"] = approved_df["Insurance Type"].astype(str).str.strip()
approved_df["Insurance Type"] = approved_df["Insurance Type"].replace({
    "Uninsurred":"Uninsured",
    "Unisured":"Uninsured",
    "MEdicare":"Medicare",
    "medicaid":"Medicaid",
    "Missing":"Missing",
    "missing":"Missing",
    "NA":"Missing",
    "N/A":"Missing",
    "Nan": "Missing",
    "nan": "Missing",
    "": "Missing"
})

approved_df["Insurance Type"] = approved_df["Insurance Type"].fillna("Missing")

#Median household income. This section is based on the median household income estimated by the Census Data
#So: one group is less than 833 monthly; the other is 833 < value <6,215; then value > 6,215

# Clean and categorize income
def categorize_income(val):
    try:
        income = float(str(val).replace(',', '').replace('$', '').strip())
        if income <= 833:
            return 'Low (≤ $833)'
        elif income <= 6215:
            return 'Middle ($834–$6,215)'
        else:
            return 'High (> $6,215)'
    except:
        return 'Missing'

approved_df['Income Category'] = approved_df['Total Household Gross Monthly Income'].apply(categorize_income)

def clean_amount(val):
    try:
        return float(str(val).replace(',', '').replace('$', '').strip())
    except:
        return 0.0

approved_df['Cleaned Amount'] = approved_df['Amount'].apply(clean_amount)

#Cleaining by Race

def clean_race(race):
    race_str = str(race).strip().lower()
    if not race or race_str in ["", "nan", "none", "missing"]:
        return "Missing"
    elif race_str == "whiate":
        return "White"
    elif race_str in [
        "american indian or alaksa native",
        "american indian or alaskan native"
    ]:
        return "American Indian or Alaska Native"
    else:
        return race.strip()

approved_df['Cleaned Race'] = approved_df['Race'].apply(clean_race)

# Group and sum amount by cleaned race
amount_by_race = approved_df.groupby('Cleaned Race')['Cleaned Amount'].sum().sort_values(ascending=False)

# Create DataFrame with totals and percentages by Race
total_amount = amount_by_race.sum()
race_df = amount_by_race.reset_index()
race_df.columns = ['Race', 'Total Amount']
race_df['Percentage'] = (race_df['Total Amount'] / total_amount * 100).round(1)

# Format as currency
race_df['Total Amount'] = race_df['Total Amount'].apply(lambda x: f"${x:,.2f}")
race_df['Percentage'] = race_df['Percentage'].astype(str) + '%'

#GROUPING DATA


# Count each category
income_counts = approved_df['Income Category'].value_counts().reindex(
    ['Low (≤ $833)', 'Middle ($834–$6,215)', 'High (> $6,215)', 'Missing'], fill_value=0
)

#Groping data according to cities

city_amount_summary = (
    approved_df.groupby("Pt City", dropna=False)["Amount"]
    .sum()
    .reset_index()
    .sort_values("Amount", ascending=False)
)

city_amount_display = city_amount_summary.copy()
city_amount_display["Amount"] = city_amount_display["Amount"].apply(lambda x: f"${x:,.2f}")


#Groping data according to gender, including percentages

gender_amount = (
    approved_df.groupby("Gender")["Amount"]
    .sum()
    .reset_index()
)

total_amount = gender_amount["Amount"].sum()
gender_amount["Percentage"] = (gender_amount["Amount"] / total_amount) * 100

gender_amount["Label"]= gender_amount.apply(lambda row: f"{row['Gender']}: {row['Percentage']:.1f}%", axis=1)

#Groping data according to top 10 cities
top10_cities = city_amount_summary.head(10)
top10_display = top10_cities.copy()
top10_display["Amount"] = top10_cities["Amount"].apply(lambda x: f"${x:,.2f}")

insurance_type_amount = (
    approved_df.groupby("Insurance Type")["Amount"]
    .sum()
    .reset_index()
)

#Groping data according to insurance type

total_amount = insurance_type_amount["Amount"].sum()
insurance_type_amount["Percentage"] = (insurance_type_amount["Amount"] / total_amount) * 100
insurance_display = insurance_type_amount.copy()
insurance_display["Amount"] = insurance_display["Amount"].apply(lambda x: f"${x:,.2f}")
insurance_display["Percentage"] = insurance_display["Percentage"].apply(lambda x: f"{x:.1f}%")

#Grouping by median household income

amount_by_category = approved_df.groupby('Income Category')['Cleaned Amount'].sum().reindex(
    ['Low (≤ $833)', 'Middle ($834–$6,215)', 'High (> $6,215)', 'Missing'], fill_value=0
)

# Grouping and sum amount by cleaned race
amount_by_race = approved_df.groupby('Cleaned Race')['Cleaned Amount'].sum().sort_values(ascending=False)


#st.write("Debug: Top 10 Cities DataFrame")
#st.write(top10_cities.columns)

#PLOTTING

#This page includes some figures for the daschboard
bar_chart = (
    alt.Chart(top10_cities)
    .mark_bar()
    .encode(
        y=alt.Y("Pt City:N", sort="-x", title="City"),
        x=alt.X("Amount:Q", title="Total Amount"),
        tooltip=["Pt City", "Amount"]
    )
    .properties(
        title="Top 10 Cities by Total Amount (Horizontal Bar Chart)",
        width=600,
        height=400
    )
)

pie_chart = (
    alt.Chart(gender_amount)
    .mark_arc(innerRadius=60)
    .encode(
        theta=alt.Theta(field="Amount", type="quantitative"),
        color=alt.Color("Gender", type="nominal"),
        tooltip=["Gender", "Amount", alt.Tooltip("Percentage", format=".1f")]
    )
    .properties(
        title="Gender Distribution",
        width=300,
        height=300
    )
)

#st.subheader("Top 10 Cities by Total Amount")
#st.dataframe(top10_cities)

#PREPARING INFO TO SHOW IN STREAMLIT

#Data Frames go first
st.title("Financial Overview")
st.subheader("Total Amount by Beneficiary City")
st.dataframe(city_amount_display)

st.subheader("Amount by Type of Insurance")
st.dataframe(insurance_display)

st.subheader('Total Amount and Percentage by Race')
st.dataframe(race_df)

#Now charts
st.subheader("Top 10 Cities by Total Amount - Bar Chart")
st.altair_chart(bar_chart, use_container_width=True)

st.subheader("Gender Distribution")
st.altair_chart(pie_chart, use_container_width=False)

st.subheader('Distribution by Household Monthly Income')
fig, ax = plt.subplots()
ax.pie(amount_by_category, labels=amount_by_category.index, autopct='%1.1f%%', startangle=90)
ax.axis('equal')
st.pyplot(fig)
