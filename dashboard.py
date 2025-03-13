import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

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
