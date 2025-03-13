import streamlit as st
import pandas as pd
import numpy as np

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
st.bar_chart(chart_data.set_index("Category"), color=chart_data["Category"].map(colors))

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
    st.write(f"**Revenue:** ${company_data['Revenue']:,.2f}")
    st.write(f"**EBITDA:** ${company_data['EBITDA']:,.2f}")
with cols[1]:
    st.write(f"**Total Debt:** ${company_data['Total Debt']:,.2f}")
    st.write(f"**Interest Expense:** ${company_data['Interest Expense']:,.2f}")
with cols[2]:
    st.write(f"**Cash Flow:** ${company_data['Cash Flow from Operations']:,.2f}")
st.write(f"**Leverage Ratio:** {company_data['Leverage Ratio']:.2f}")
st.write(f"**Interest Coverage:** {company_data['Interest Coverage']:.2f}")
st.write(f"**EBITDA Margin:** {company_data['EBITDA Margin']:.2%}")
st.write(f"**Category:** **{company_data['Category']}**", unsafe_allow_html=True)

qualitative_notes = {
    "TWLO": "Facing competition from new entrants.",
    "PD": "Negative EBITDA due to R&D investments.",
    "BOX": "Stable but high leverage from acquisition.",
    "TDOC": "Regulatory uncertainty in telehealth.",
    "AMWL": "Cash burn from expansion efforts.",
    "HIMS": "Strong growth but unproven scalability.",
    "MAN": "Cyclical risks in staffing market.",
    "RHI": "Resilient despite economic slowdown.",
    "ASGN": "Consistent performance with low debt."
}
st.write(f"**Qualitative Notes:** {qualitative_notes[selected_company]}")

if st.button("Export Company Data to CSV"):
    company_data.to_csv(f"data/{selected_company}_export.csv")
    st.success(f"Exported data for {selected_company} to 'data/{selected_company}_export.csv'")

st.header("Scenario Analysis")
st.write("Simulate the impact of interest rate changes on portfolio health.")
interest_rate_change = st.slider("Change in Interest Rate (%)", -5.0, 5.0, 0.0, 0.01)
new_interest_expense = company_data["Interest Expense"] * (1 + interest_rate_change / 100)
new_coverage = company_data["EBITDA"] / new_interest_expense if new_interest_expense > 0 else float('inf')
st.write(f"New Interest Coverage with {interest_rate_change:.2f}% rate change: {new_coverage:.2f}")

revenue_decline = st.slider("Revenue Decline (%)", 0.0, 50.0, 0.0, 1.0)
new_revenue = company_data["Revenue"] * (1 - revenue_decline / 100)
new_ebitda = company_data["EBITDA"] * (1 - revenue_decline / 100)  # Assume proportional EBITDA drop
new_leverage = company_data["Total Debt"] / new_ebitda if new_ebitda != 0 else float('inf')
st.write(f"New Leverage Ratio with {revenue_decline:.1f}% revenue decline: {new_leverage:.2f}")

st.write("**Footnote:** The scenario analysis adjusts Interest Coverage based on rate changes (e.g., 0.01% shift reflects a small market move) and Leverage Ratio based on revenue declines. This is a hypothetical portfolio—adjust thresholds or add real qualitative data for operational use.")

st.header("Performance Trends")
years = ["2021", "2022", "2023"]
trend_data = pd.DataFrame({
    "Year": years * len(filtered_df),
    "Revenue": np.random.normal(company_data["Revenue"], company_data["Revenue"] * 0.1, 3) if company_data["Revenue"] else [0, 0, 0],
    "Company": [selected_company] * 3
})
st.line_chart(trend_data.set_index("Year")["Revenue"])

st.subheader("Risk Score")
risk_score = (company_data["Leverage Ratio"] * 0.4 + (1 / company_data["Interest Coverage"] if company_data["Interest Coverage"] != 0 else 10) * 0.4 + (1 - company_data["EBITDA Margin"]) * 0.2) * 100
st.write(f"Risk Score: {risk_score:.2f} (Lower is better; scale 0-100)")
