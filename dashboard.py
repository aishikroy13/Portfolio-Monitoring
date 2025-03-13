import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

df = pd.read_csv("data/analyzed_portfolio.csv")

st.title("Private Credit Portfolio Monitoring Dashboard")
st.write("Interactive dashboard to monitor a hypothetical direct lending portfolio of 9 companies.")

colors = {
    "Green": "#00FF00",  # Bright Green
    "Yellow": "#FFFF00", # Bright Yellow
    "Amber": "#FFA500",  # Orange (Amber)
    "Red": "#FF0000"     # Bright Red
}

st.header("Portfolio Overview")
total_assets = len(df)
risk_distribution = df["Category"].value_counts()

st.write(f"Total Assets: {total_assets}")
chart_data = pd.DataFrame({
    "Category": risk_distribution.index,
    "Count": risk_distribution.values
})
chart_data["Color"] = chart_data["Category"].map(colors)

bar_chart = alt.Chart(chart_data).mark_bar().encode(
    x=alt.X("Count:Q", title="Number of Companies"),
    y=alt.Y("Category:N", title="Category"),
    color=alt.Color("Color:N", scale=None, legend=None)
).properties(
    width=600,
    height=300
)
st.altair_chart(bar_chart)

selected_category = st.selectbox("Filter by Category", ["All"] + list(df["Category"].unique()))
if selected_category == "All":
    filtered_df = df
else:
    filtered_df = df[df["Category"] == selected_category]

df["Sector"] = df["Company"].map({
    "TWLO": "Technology", "PD": "Technology", "BOX": "Technology",
    "TDOC": "Healthcare", "AMWL": "Healthcare", "HIMS": "Healthcare",
    "MAN": "Services", "RHI": "Services", "ASGN": "Services"
})
selected_sector = st.multiselect("Filter by Sector", ["All"] + list(df["Sector"].unique()), default="All")
if "All" not in selected_sector and selected_sector:
    filtered_df = filtered_df[filtered_df["Sector"].isin(selected_sector)]

st.header("Company Details")
selected_company = st.selectbox("Select a Company", filtered_df["Company"])
company_data = filtered_df[filtered_df["Company"] == selected_company].iloc[0]

st.subheader(f"{selected_company} Financial Health")
cols = st.columns(3)
with cols[0]:
    st.write(f"**Revenue:** ${company_data['Revenue']:,.2f}", style="color: #00CED1")  # Cyan
    st.write(f"**EBITDA:** ${company_data['EBITDA']:,.2f}", style="color: #00CED1")
with cols[1]:
    st.write(f"**Total Debt:** ${company_data['Total Debt']:,.2f}", style="color: #FF69B4")  # Pink
    st.write(f"**Interest Expense:** ${company_data['Interest Expense']:,.2f}", style="color: #FF69B4")
with cols[2]:
    st.write(f"**Cash Flow:** ${company_data['Cash Flow from Operations']:,.2f}", style="color: #7FFF00")  # Chartreuse
    st.write(f"**Leverage Ratio:** {company_data['Lever
