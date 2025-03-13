import streamlit as st
import pandas as pd

df = pd.read_csv("data/analyzed_portfolio.csv")

st.title("Private Credit Portfolio Monitoring Dashboard")
st.write("Interactive dashboard to monitor a hypothetical direct lending portfolio of 9 companies.")

st.header("Portfolio Overview")
total_assets = len(df)
risk_distribution = df["Category"].value_counts()
st.write(f"Total Assets: {total_assets}")
st.bar_chart(risk_distribution)

selected_category = st.selectbox("Filter by Category", ["All"] + list(df["Category"].unique()))
if selected_category == "All":
    filtered_df = df
else:
    filtered_df = df[df["Category"] == selected_category]

st.header("Company Details")
selected_company = st.selectbox("Select a Company", filtered_df["Company"])
company_data = filtered_df[filtered_df["Company"] == selected_company].iloc[0]

st.subheader(f"{selected_company} Financial Health")
st.write(f"**Revenue:** ${company_data['Revenue']:,.2f}")
st.write(f"**EBITDA:** ${company_data['EBITDA']:,.2f}")
st.write(f"**Total Debt:** ${company_data['Total Debt']:,.2f}")
st.write(f"**Interest Expense:** ${company_data['Interest Expense']:,.2f}")
st.write(f"**Cash Flow from Operations:** ${company_data['Cash Flow from Operations']:,.2f}")
st.write(f"**Leverage Ratio:** {company_data['Leverage Ratio']:.2f}")
st.write(f"**Interest Coverage:** {company_data['Interest Coverage']:.2f}")
st.write(f"**EBITDA Margin:** {company_data['EBITDA Margin']:.2%}")
st.write(f"**Category:** {company_data['Category']}")

st.header("Scenario Analysis")
interest_rate_change = st.slider("Change in Interest Rate (%)", -5.0, 5.0, 0.0)
new_interest_expense = company_data["Interest Expense"] * (1 + interest_rate_change / 100)
new_coverage = company_data["EBITDA"] / new_interest_expense if new_interest_expense > 0 else float('inf')
st.write(f"New Interest Coverage with {interest_rate_change}% rate change: {new_coverage:.2f}")

st.write("Note: This is a hypothetical portfolio for demonstration. Adjust thresholds or add qualitative data for real-world use.")
