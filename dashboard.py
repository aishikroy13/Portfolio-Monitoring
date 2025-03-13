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


st.header("Metric Comparison Visualization")
if not filtered_df.empty:
    # Use the metrics selected in the Portfolio Comparison section
    if 'metrics_to_compare' in locals() and metrics_to_compare:
        selected_metrics = metrics_to_compare
    else:
        # Default metrics if none selected
        selected_metrics = ["Leverage Ratio", "Interest Coverage"]
    
    # Filter to selected companies
    if 'selected_company' in locals() and selected_company:
        chart_data = filtered_df[filtered_df["Company"] == selected_company].copy()
    else:
        chart_data = filtered_df.copy()
    
    # Create normalized data for visualization
    normalized_data = []
    
    for _, company_row in chart_data.iterrows():
        company_name = company_row["Company"]
        
        for metric in selected_metrics:
            try:
                value = float(company_row[metric])
                
                # Handle special cases for proper normalization
                if metric == "EBITDA Margin":
                    # Higher is better for margins, normalize to 0-1 (assuming margin between -100% and 100%)
                    normalized_value = (value + 1) / 2 if value < 0 else value
                elif metric == "Interest Coverage":
                    # Higher is better for coverage, cap at 20 for normalization
                    normalized_value = min(max(value, 0), 20) / 20
                elif metric == "Leverage Ratio":
                    # Lower is better for leverage, cap at 10 for normalization
                    # Invert so higher values = better (for consistent color scheme)
                    normalized_value = 1 - (min(max(value, 0), 10) / 10)
                elif metric in ["Revenue", "EBITDA"]:
                    # For revenue/EBITDA, normalize relative to the dataset
                    all_values = filtered_df[metric].astype(float)
                    min_val, max_val = all_values.min(), all_values.max()
                    # For negative EBITDA, treat worse than zero
                    if metric == "EBITDA" and value < 0:
                        norm_val = value / min_val if min_val < 0 else 0
                        normalized_value = 0.5 * (1 + norm_val)  # Scale to 0-0.5 range
                    else:
                        # Regular normalization for positive values
                        range_val = max_val - min_val
                        normalized_value = (value - min_val) / range_val if range_val > 0 else 0.5
                else:
                    # Generic normalization (min-max scaling)
                    all_values = filtered_df[metric].astype(float)
                    min_val, max_val = all_values.min(), all_values.max()
                    range_val = max_val - min_val
                    normalized_value = (value - min_val) / range_val if range_val > 0 else 0.5
                
                # For visualization purposes, ensure values are in 0-1 range
                normalized_value = max(0, min(normalized_value, 1))
                
                normalized_data.append({
                    "Company": company_name,
                    "Metric": metric,
                    "Original_Value": value,
                    "Normalized_Value": normalized_value
                })
            except (ValueError, TypeError):
                # Skip if value can't be converted to float
                pass
    
    if normalized_data:
        # Create DataFrame from normalized data
        norm_df = pd.DataFrame(normalized_data)
        
        # Create a multi-series bar chart
        st.subheader("Metric Performance by Company")
        
        # Calculate height based on number of companies
        chart_height = max(300, len(chart_data) * 50)
        
        bar_chart = alt.Chart(norm_df).mark_bar().encode(
            x=alt.X("Normalized_Value:Q", title="Normalized Value (0-1)"),
            y=alt.Y("Company:N", title="Company"),
            color=alt.Color("Metric:N", 
                           scale=alt.Scale(scheme="category10"),
                           legend=alt.Legend(title="Metrics")),
            tooltip=["Company", "Metric", "Original_Value:Q", "Normalized_Value:Q"]
        ).properties(
            width=600,
            height=chart_height
        )
        
        st.altair_chart(bar_chart, use_container_width=True)
        
        # Create a scatter plot matrix for the metrics
        if len(chart_data) > 1 and len(selected_metrics) > 1:
            st.subheader("Metric Relationship Matrix")
            
            # Prepare data for scatter plot matrix
            metrics_data = chart_data[["Company"] + selected_metrics].copy()
            
            # Convert to numeric
            for metric in selected_metrics:
                metrics_data[metric] = pd.to_numeric(metrics_data[metric], errors='coerce')
            
            # Remove any rows with NaN values
            metrics_data = metrics_data.dropna()
            
            if not metrics_data.empty and len(metrics_data) > 1:
                # Melt the data for the scatter plot matrix
                melted_data = pd.melt(
                    metrics_data, 
                    id_vars=["Company"], 
                    value_vars=selected_metrics, 
                    var_name="Metric", 
                    value_name="Value"
                )
                
                # Create a scatter plot matrix
                scatter_matrix = alt.Chart(melted_data).mark_circle(size=60).encode(
                    x=alt.X("Metric:N", title=None),
                    y=alt.Y("Value:Q", title=None),
                    color="Company:N",
                    tooltip=["Company", "Metric", "Value:Q"]
                ).properties(
                    width=600,
                    height=400
                ).facet(
                    column=alt.Column("Metric:N", title=None),
                    row=alt.Row("Metric:N", title=None)
                )
                
                st.altair_chart(scatter_matrix, use_container_width=True)
    else:
        st.warning("No valid data available for visualization.")
else:
    st.warning("No data available for visualization.")
