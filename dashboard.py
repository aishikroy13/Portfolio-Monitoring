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
    st.write(f"**Revenue:** ${company_data['Revenue']:,.2f}")
    st.write(f"**EBITDA:** ${company_data['EBITDA']:,.2f}")
with cols[1]:
    st.write(f"**Total Debt:** ${company_data['Total Debt']:,.2f}")
    st.write(f"**Interest Expense:** ${company_data['Interest Expense']:,.2f}")
with cols[2]:
    st.write(f"**Cash Flow:** ${company_data['Cash Flow from Operations']:,.2f}")
    st.write(f"**Leverage Ratio:** {company_data['Leverage Ratio']:.2f}")  # Fixed missing bracket
st.write(f"**Interest Coverage:** {company_data['Interest Coverage']:.2f}")
st.write(f"**EBITDA Margin:** {company_data['EBITDA Margin']:.2%}")
category_color = colors.get(company_data["Category"], "#FFFFFF")  # Default to white if category not found
st.markdown(f"**Category:** <span style='color:{category_color}'>{company_data['Category']}</span>", unsafe_allow_html=True)

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
    company_data.to_frame().T.to_csv(f"data/{selected_company}_export.csv", index=False)
    st.success(f"Exported data for {selected_company} to 'data/{selected_company}_export.csv'")

st.header("Scenario Analysis")
st.write("Simulate the impact of market changes on portfolio health.")

interest_rate_change = st.slider("Change in Interest Rate (%)", -5.0, 5.0, 0.0, 0.01, key="interest_slider")
new_interest_expense = company_data["Interest Expense"] * (1 + interest_rate_change / 100)
new_coverage = company_data["EBITDA"] / new_interest_expense if new_interest_expense > 0 else float('inf')
st.write(f"New Interest Coverage with {interest_rate_change:.2f}% rate change: {new_coverage:.2f}")

revenue_decline = st.slider("Revenue Decline (%)", 0.0, 50.0, 0.0, 1.0, key="revenue_slider")
new_revenue = company_data["Revenue"] * (1 - revenue_decline / 100)
new_ebitda = company_data["EBITDA"] * (1 - revenue_decline / 100)  # Assume proportional EBITDA drop
new_leverage = company_data["Total Debt"] / new_ebitda if new_ebitda != 0 else float('inf')
st.write(f"New Leverage Ratio with {revenue_decline:.1f}% revenue decline: {new_leverage:.2f}")

st.markdown("**Footnote:** The Interest Rate Slider adjusts Interest Expense to simulate market rate changes (e.g., 0.01% reflects a minor shift), recalculating Interest Coverage (EBITDA / New Interest Expense). The Revenue Decline Slider reduces Revenue and EBITDA proportionally, updating Leverage Ratio (Total Debt / New EBITDA) to model economic downturns. This is a hypothetical portfolio—adjust thresholds or add qualitative data for real-world use.")

st.header("Performance Trends")
years = ["2021", "2022", "2023"]
trend_data = pd.DataFrame({
    "Year": years * len(filtered_df),
    "Revenue": np.concatenate([np.random.normal(company_data["Revenue"], company_data["Revenue"] * 0.1, 3) for _ in range(len(filtered_df))]),
    "EBITDA": np.concatenate([np.random.normal(company_data["EBITDA"], abs(company_data["EBITDA"]) * 0.1, 3) for _ in range(len(filtered_df))]),
    "Company": [selected_company] * 3
})
revenue_chart = alt.Chart(trend_data).mark_line(color="#00CED1").encode(
    x="Year",
    y="Revenue",
    tooltip=["Year", "Revenue"]
).properties(
    title="Revenue Trend",
    width=600,
    height=300
)
ebitda_chart = alt.Chart(trend_data).mark_line(color="#FF69B4").encode(
    x="Year",
    y="EBITDA",
    tooltip=["Year", "EBITDA"]
).properties(
    title="EBITDA Trend",
    width=600,
    height=300
)
st.altair_chart(revenue_chart)
st.altair_chart(ebitda_chart)

st.subheader("Risk Score")
if company_data["Interest Coverage"] != 0:
    risk_score = (company_data["Leverage Ratio"] * 0.4 + (1 / company_data["Interest Coverage"]) * 0.4 + (1 - company_data["EBITDA Margin"]) * 0.2) * 100
else:
    risk_score = (company_data["Leverage Ratio"] * 0.4 + 10 * 0.4 + (1 - company_data["EBITDA Margin"]) * 0.2) * 100
st.write(f"Risk Score: {risk_score:.2f} (Lower is better; scale 0-100)")

st.header("Portfolio Comparison")
metrics_to_compare = st.multiselect("Select Metrics to Compare", ["Revenue", "EBITDA", "Leverage Ratio", "Interest Coverage", "EBITDA Margin"], default=["Leverage Ratio", "Interest Coverage"])
st.write(filtered_df[["Company"] + metrics_to_compare])

st.header("Risk Heatmap")
heatmap_data = filtered_df[["Company", "Leverage Ratio", "Interest Coverage"]].melt(id_vars=["Company"], value_vars=["Leverage Ratio", "Interest Coverage"])
heatmap = alt.Chart(heatmap_data).mark_rect().encode(
    x="Company",
    y="variable",
    color=alt.Color("value:Q", scale=alt.Scale(scheme="redyellowgreen")),
    tooltip=["Company", "variable", "value"]
).properties(
    width=600,
    height=200
)
st.altair_chart(heatmap)
