import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import List
import asyncio
import sys
from pathlib import Path
import pandas as pd

# Add the src directory to the Python path
src_path = str(Path(__file__).parent.parent)
if src_path not in sys.path:
    sys.path.append(src_path)

from src.api import PopulationAPIClient, PopulationData
from src.analysis import analyze_population_trends, filter_by_growth_rate, export_to_csv

# Page config
st.set_page_config(
    page_title="World Population Analysis",
    page_icon="🌍",
    layout="wide"
)

# Title
st.title("🌍 World Population Analysis")
st.markdown("""
This dashboard analyzes population data from the World Bank API.
Select a country and date range to view population trends and statistics.
""")

# Sidebar
st.sidebar.header("Settings")

# Country selection
country_code = st.sidebar.text_input(
    "Country Code (e.g., USA, CHN, IND)",
    value="USA"
).upper()

# Year range selection
col1, col2 = st.sidebar.columns(2)
with col1:
    start_year = st.number_input(
        "Start Year",
        min_value=1960,
        max_value=2023,
        value=2000
    )
with col2:
    end_year = st.number_input(
        "End Year",
        min_value=1960,
        max_value=2023,
        value=2023
    )

# Initialize API client
client = PopulationAPIClient(rate_limit=10, time_window=1)

async def get_data():
    """Fetch and process population data."""
    data = await client.calculate_growth_rate(
        country_code,
        start_year,
        end_year
    )
    return data

# Main content
if st.sidebar.button("Analyze"):
    with st.spinner("Fetching data..."):
        # Run async function
        data = asyncio.run(get_data())
        
        if not data:
            st.error("No data available for the selected parameters.")
            st.stop()
        
        # Display analysis
        analysis = analyze_population_trends(data)
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Average Growth Rate",
                f"{analysis.average_growth_rate:.2f}%"
            )
        with col2:
            st.metric(
                "Total Change",
                f"{analysis.total_change:,}"
            )
        with col3:
            st.metric(
                "Percentage Change",
                f"{analysis.percentage_change:.2f}%"
            )
        with col4:
            st.metric(
                "Current Population",
                f"{analysis.max_population:,}"
            )
        
        # Population trend chart
        st.subheader("Population Trend")
        fig = px.line(
            x=[d.year for d in data],
            y=[d.population for d in data],
            labels={'x': 'Year', 'y': 'Population'},
            title=f"Population Trend for {country_code}",
            template='plotly_white'
        )
        # Format y-axis to show numbers in millions
        fig.update_yaxes(
            tickformat=",.0f",
            title="Population"
        )
        # Format x-axis
        fig.update_xaxes(
            title="Year",
            dtick=5  # Show ticks every 5 years
        )
        # Add hover information
        fig.update_traces(
            hovertemplate="<br>".join([
                "Year: %{x}",
                "Population: %{y:,.0f}",
                "<extra></extra>"
            ])
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Growth rate chart
        st.subheader("Growth Rate")
        growth_data = [(d.year, d.growth_rate) for d in data if d.growth_rate is not None]
        if growth_data:
            years, rates = zip(*growth_data)
            fig = px.line(
                x=years,
                y=rates,
                labels={'x': 'Year', 'y': 'Growth Rate (%)'},
                title=f"Population Growth Rate for {country_code}",
                template='plotly_white'
            )
            # Format y-axis
            fig.update_yaxes(
                tickformat=".2f",
                title="Growth Rate (%)"
            )
            # Format x-axis
            fig.update_xaxes(
                title="Year",
                dtick=5
            )
            # Add hover information
            fig.update_traces(
                hovertemplate="<br>".join([
                    "Year: %{x}",
                    "Growth Rate: %{y:.2f}%",
                    "<extra></extra>"
                ])
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No growth rate data available for the selected period.")
        
        # Data table
        st.subheader("Raw Data")
        df = pd.DataFrame([
            {
                'Year': d.year,
                'Population': d.population,
                'Growth Rate (%)': f"{d.growth_rate:.2f}" if d.growth_rate is not None else "N/A"
            }
            for d in data
        ])
        # Format the population column
        df['Population'] = df['Population'].apply(lambda x: f"{x:,.0f}")
        st.dataframe(df, use_container_width=True)
        
        # Export button
        if st.button("Export to CSV"):
            export_to_csv(data, f"population_data_{country_code}.csv")
            st.success("Data exported successfully!") 