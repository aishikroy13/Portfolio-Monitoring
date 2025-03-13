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

df["Sector"] = df["Company"].map({
    "TWLO": "Technology", "PD": "Technology", "BOX": "Technology",
    "TDOC": "Healthcare", "AMWL": "Healthcare", "HIMS": "Healthcare",
    "MAN": "Services", "RHI": "Services", "ASGN": "Services"
})

selected_category = st.selectbox("Filter by Category", ["All"] + list(df["Category"].unique()), key="category_filter")
if selected_category == "All":
    filtered_df = df
else:
    filtered_df = df[df["Category"] == selected_category]

selected_sector = st.multiselect("Filter by Sector", ["All"] + list(df["Sector"].unique()), default="All", key="sector_filter")
if "All" not in selected_sector and selected_sector:
    filtered_df = filtered_df[filtered_df["Sector"].isin(selected_sector)]

st.header("Company Details")

if filtered_df.empty:
    st.warning("No companies match the selected filters. Please adjust your filter criteria.")
else:
    selected_company = st.selectbox("Select a Company", filtered_df["Company"].tolist(), key="company_selector")
    
    if selected_company:
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
        category_color = colors.get(company_data["Category"], "#FFFFFF")
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

if not filtered_df.empty and 'selected_company' in locals() and selected_company:
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

if not filtered_df.empty and 'selected_company' in locals() and selected_company:
    years = ["2021", "2022", "2023"]

    # Fix: Only generate trend data for the selected company
    trend_data = pd.DataFrame({
        "Year": years,
        "Revenue": np.random.normal(company_data["Revenue"], company_data["Revenue"] * 0.1, 3),
        "EBITDA": np.random.normal(company_data["EBITDA"], abs(company_data["EBITDA"]) * 0.1, 3),
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

if not filtered_df.empty:
    metrics_to_compare = st.multiselect(
        "Select Metrics to Compare", 
        ["Revenue", "EBITDA", "Leverage Ratio", "Interest Coverage", "EBITDA Margin"], 
        default=["Leverage Ratio", "Interest Coverage"], 
        key="metrics_selector"
    )
    
    if metrics_to_compare:
        display_df = filtered_df[["Company"] + metrics_to_compare].copy()
        
        for col in metrics_to_compare:
            if col in ["Revenue", "EBITDA"]:
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")
            elif col == "EBITDA Margin":
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}")
            else:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}")
        
        st.write(display_df)

st.header("Risk Heatmap")
if not filtered_df.empty:
    if 'metrics_to_compare' in locals() and metrics_to_compare:
        heatmap_metrics = metrics_to_compare
    else:
        heatmap_metrics = ["Leverage Ratio", "Interest Coverage"]
    
    if len(heatmap_metrics) > 0:
        # Create heatmap with all selected metrics
        heatmap_data = filtered_df[["Company"] + heatmap_metrics].melt(
            id_vars=["Company"], 
            value_vars=heatmap_metrics
        )
        
        higher_is_better = ["Interest Coverage", "Revenue", "EBITDA", "EBITDA Margin"]
        lower_is_better = ["Leverage Ratio"]
        
        min_values = {}
        max_values = {}
        
        for metric in heatmap_metrics:
            min_values[metric] = filtered_df[metric].min()
            max_values[metric] = filtered_df[metric].max()
        
        def normalize_value(row):
            metric = row['variable']
            value = row['value']
            
            if min_values[metric] == max_values[metric]:
                return 0.5
                
            if metric in higher_is_better:
                return (value - min_values[metric]) / (max_values[metric] - min_values[metric])
            else:
                return 1 - ((value - min_values[metric]) / (max_values[metric] - min_values[metric]))

        heatmap_data['normalized_value'] = heatmap_data.apply(normalize_value, axis=1)

        heatmap = alt.Chart(heatmap_data).mark_rect().encode(
            x="Company:N",
            y="variable:N",
            color=alt.Color(
                "normalized_value:Q", 
                scale=alt.Scale(domain=[0, 1], scheme="redyellowgreen-9"),  # Fixed scheme name
                legend=alt.Legend(title="Risk Level")
            ),
            tooltip=["Company", "variable", "value"]
        ).properties(
            width=600,
            height=len(heatmap_metrics) * 40  # Dynamic height based on number of metrics
        )
        
        st.altair_chart(heatmap)
    else:
        st.warning("Please select at least one metric to display in the heatmap.")
