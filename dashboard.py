import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

df = pd.read_csv("data/analyzed_portfolio.csv")
# Initialize filtered_df right after loading the data
filtered_df = df.copy()

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

# Add Sector column to the original DataFrame first
df["Sector"] = df["Company"].map({
    "TWLO": "Technology", "PD": "Technology", "BOX": "Technology",
    "TDOC": "Healthcare", "AMWL": "Healthcare", "HIMS": "Healthcare",
    "MAN": "Services", "RHI": "Services", "ASGN": "Services"
})

# Apply category filter - just once
selected_category = st.selectbox("Filter by Category", ["All"] + list(df["Category"].unique()), key="category_filter")
if selected_category == "All":
    filtered_df = df
else:
    filtered_df = df[df["Category"] == selected_category]

# Then apply sector filter to the already filtered DataFrame
selected_sector = st.multiselect("Filter by Sector", ["All"] + list(df["Sector"].unique()), default="All", key="sector_filter")
if "All" not in selected_sector and selected_sector:
    filtered_df = filtered_df[filtered_df["Sector"].isin(selected_sector)]

st.header("Company Details")

# Check if filtered_df is empty
if filtered_df.empty:
    st.warning("No companies match the selected filters. Please adjust your filter criteria.")
else:
    selected_company = st.selectbox("Select a Company", filtered_df["Company"].tolist(), key="company_selector")
    
    # Get the company data only if there's a valid selection
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

# Only show scenario analysis if a company is selected
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

# Only show performance trends if a company is selected
if not filtered_df.empty and 'selected_company' in locals() and selected_company:
    years = ["2021", "2022", "2023"]

    # Generate trend data for selected company only if EBITDA is positive
    # For companies with negative EBITDA, use absolute value for display
    ebitda_value = abs(company_data["EBITDA"])
    ebitda_fluctuation = ebitda_value * 0.1 if ebitda_value > 0 else 1000000
    
    trend_data = pd.DataFrame({
        "Year": years,
        "Revenue": np.random.normal(company_data["Revenue"], abs(company_data["Revenue"] * 0.1), 3),
        "EBITDA": np.random.normal(company_data["EBITDA"], ebitda_fluctuation, 3),
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
    
    # Completely revised risk score calculation
    # Handle negative or zero EBITDA
    if company_data["EBITDA"] <= 0:
        ebitda_factor = 20  # Maximum risk for negative EBITDA
    else:
        # Calculate EBITDA margin component - cap between 0-20
        margin = company_data["EBITDA Margin"]
        ebitda_factor = max(0, min(20, 20 * (1 - margin)))
    
    # Handle negative or zero Interest Coverage
    if company_data["Interest Coverage"] <= 0:
        coverage_factor = 40  # Maximum risk for negative coverage
    else:
        # Calculate coverage component - cap between 0-40
        coverage = min(company_data["Interest Coverage"], 10)  # Cap at 10x
        coverage_factor = max(0, min(40, 40 * (1 - coverage/10)))
    
    # Handle negative Leverage Ratio
    if company_data["Leverage Ratio"] < 0:
        leverage_factor = 20  # Medium risk for negative leverage (could be good or bad)
    else:
        # Calculate leverage component - cap between 0-40
        leverage = min(company_data["Leverage Ratio"], 8)  # Cap at 8x
        leverage_factor = max(0, min(40, 5 * leverage))
    
    # Sum all components to get final score
    risk_score = ebitda_factor + coverage_factor + leverage_factor
    
    # Ensure score is between 0-100
    risk_score = max(0, min(100, risk_score))
    
    st.write(f"Risk Score: {risk_score:.2f} (Lower is better; scale 0-100)")

st.header("Portfolio Comparison")

# Only show if filtered_df is not empty
if not filtered_df.empty:
    metrics_to_compare = st.multiselect(
        "Select Metrics to Compare", 
        ["Revenue", "EBITDA", "Leverage Ratio", "Interest Coverage", "EBITDA Margin"], 
        default=["Leverage Ratio", "Interest Coverage"], 
        key="metrics_selector"
    )
    
    if metrics_to_compare:
        # Format the displayed data for better readability
        display_df = filtered_df[["Company"] + metrics_to_compare].copy()
        
        # Format numerical columns based on their type
        for col in metrics_to_compare:
            if col in ["Revenue", "EBITDA"]:
                # Format large currency values
                display_df[col] = display_df[col].apply(lambda x: f"${x:,.2f}")
            elif col == "EBITDA Margin":
                # Format percentages
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2%}")
            else:
                # Format ratios to 2 decimal places
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}")
        
        st.write(display_df)


st.header("Risk Heatmap")
if not filtered_df.empty:
    # Filter to the selected company if one is chosen
    if 'selected_company' in locals() and selected_company:
        heatmap_data = filtered_df[filtered_df["Company"] == selected_company][["Company"] + df.columns.tolist()].copy()
    else:
        heatmap_data = filtered_df[["Company"] + df.columns.tolist()].copy()
    
    # Define metrics for the heatmap (adjust based on your app's logic)
    heatmap_metrics = ["Leverage Ratio", "Interest Coverage"]  # Example; use your selected metrics
    heatmap_data = heatmap_data[["Company"] + heatmap_metrics]
    
    # Fill NaNs with 0 in metric columns
    heatmap_data[heatmap_metrics] = heatmap_data[heatmap_metrics].fillna(0)
    
    # Melt the DataFrame
    heatmap_data = heatmap_data.melt(
        id_vars=["Company"],
        value_vars=heatmap_metrics,
        var_name="Metric",
        value_name="Value"
    )
    
    # Example normalization function (replace with your own if different)
    def normalize_value(row):
        metric = row["Metric"]
        value = row["Value"]
        metric_values = heatmap_data[heatmap_data["Metric"] == metric]["Value"]
        min_val, max_val = metric_values.min(), metric_values.max()
        if min_val == max_val:
            return 0.5
        return (value - min_val) / (max_val - min_val) if max_val > min_val else 0.5
    
    # Apply normalization and ensure numeric type
    heatmap_data["Normalized_Value"] = heatmap_data.apply(normalize_value, axis=1)
    heatmap_data["Normalized_Value"] = pd.to_numeric(heatmap_data["Normalized_Value"], errors="coerce")
    heatmap_data["Normalized_Value"] = heatmap_data["Normalized_Value"].clip(0, 1)
    
    # Clean the DataFrame
    heatmap_data = heatmap_data.dropna(subset=["Normalized_Value"])  # Drop rows with NaN in Normalized_Value
    heatmap_data = heatmap_data.reset_index(drop=True)  # Reset index to standard form
    
    # Debugging: Display data types and sample
    st.write("Heatmap Data Types:", heatmap_data.dtypes)
    st.write("Heatmap Data Sample:", heatmap_data.head())
    
    # Create and render the heatmap
    if not heatmap_data.empty:
        try:
            heatmap = alt.Chart(heatmap_data).mark_rect().encode(
                x=alt.X("Company:N", title="Company"),
                y=alt.Y("Metric:N", title="Metric"),
                color=alt.Color(
                    "Normalized_Value:Q",
                    scale=alt.Scale(domain=[0, 1], scheme="redyellowgreen"),
                    legend=alt.Legend(title="Risk Level (0-1)")
                ),
                tooltip=["Company", "Metric", "Value:Q", "Normalized_Value:Q"]
            ).properties(
                width=600,
                height=len(heatmap_metrics) * 40
            )
            st.altair_chart(heatmap, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering heatmap: {str(e)}")
            st.write("Heatmap data sample:", heatmap_data.head())
    else:
        st.warning("No valid data available for the heatmap after processing.")
else:
    st.warning("No data available to display the heatmap.")
