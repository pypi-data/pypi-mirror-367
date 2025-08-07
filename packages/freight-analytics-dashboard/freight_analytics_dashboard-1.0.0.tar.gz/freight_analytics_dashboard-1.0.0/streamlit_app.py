####### Author: Megh KC ##########
##### Streamlit Cloud Ready - Freight Analytics Dashboard #########
##### Created Date: 08/21/2024 | Enhanced: 2025 #######

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configure page settings
st.set_page_config(
    page_title="US Freight Analytics Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #2c5aa0;
        margin: 1rem 0;
        border-left: 4px solid #ff6b6b;
        padding-left: 1rem;
    }
    
    .metric-card {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .insight-box {
        background: #f8f9fa;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Data loading and caching functions
@st.cache_data
def load_rail_data():
    """Load and preprocess rail data with caching"""
    try:
        # Try multiple possible paths
        possible_paths = [
            'Data/Rail_Carloadings_originated.csv',
            './Data/Rail_Carloadings_originated.csv',
            'Rail_Carloadings_originated.csv'
        ]
        
        df = None
        for path in possible_paths:
            if os.path.exists(path):
                df = pd.read_csv(path)
                break
        
        if df is None:
            # Debug: show current directory and available files
            current_dir = os.getcwd()
            files = os.listdir('.')
            st.error(f"Rail data file not found. Current directory: {current_dir}")
            st.error(f"Available files: {files}")
            if os.path.exists('Data'):
                data_files = os.listdir('Data')
                st.error(f"Files in Data folder: {data_files}")
            return pd.DataFrame()
        
        df['Date'] = pd.to_datetime(df['Date'])
        df['Season'] = df['Month'].apply(get_season)
        return df
    except Exception as e:
        st.error(f"Error loading rail data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_port_data():
    """Load and preprocess port data with caching"""
    try:
        # Try multiple possible paths
        possible_paths = [
            'Data/port_dataset.json',
            './Data/port_dataset.json',
            'port_dataset.json'
        ]
        
        parsed_data = None
        for path in possible_paths:
            if os.path.exists(path):
                with open(path, 'r') as file:
                    parsed_data = json.load(file)
                break
        
        if parsed_data is None:
            # Debug: show current directory and available files
            current_dir = os.getcwd()
            files = os.listdir('.')
            st.error(f"Port data file not found. Current directory: {current_dir}")
            st.error(f"Available files: {files}")
            if os.path.exists('Data'):
                data_files = os.listdir('Data')
                st.error(f"Files in Data folder: {data_files}")
            return pd.DataFrame()
        
        df = pd.DataFrame(parsed_data)
        df_melted = df.melt(id_vars=["port"], var_name="port_name", value_name="TEU_values")
        df_melted['port'] = pd.to_datetime(df_melted['port'], errors='coerce')
        df_melted['TEU_values'] = pd.to_numeric(df_melted['TEU_values'], errors='coerce')
        df_melted = df_melted.dropna(subset=['TEU_values'])
        df_melted['month'] = df_melted['port'].dt.strftime('%b')
        df_melted['year'] = df_melted['port'].dt.year
        df_melted['season'] = df_melted['month'].apply(get_season_water)
        
        return df_melted
    except Exception as e:
        st.error(f"Error loading port data: {e}")
        return pd.DataFrame()

# Utility functions
def get_season(month):
    """Determine season based on month for rail data"""
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    elif month in [9, 10, 11]:
        return 'Fall'

def get_season_water(month):
    """Determine season based on month for water data"""
    if month in ['Dec', 'Jan', 'Feb']:
        return 'Winter'
    elif month in ['Mar', 'Apr', 'May']:
        return 'Spring'
    elif month in ['Jun', 'Jul', 'Aug']:
        return 'Summer'
    elif month in ['Sep', 'Oct', 'Nov']:
        return 'Fall'

def create_metric_cards(col1, col2, col3, col4, title1, value1, title2, value2, title3, value3, title4, value4):
    """Create metric cards for KPIs"""
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{title1}</h3>
            <h2>{value1}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{title2}</h3>
            <h2>{value2}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{title3}</h3>
            <h2>{value3}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{title4}</h3>
            <h2>{value4}</h2>
        </div>
        """, unsafe_allow_html=True)

# Main dashboard header
st.markdown('<h1 class="main-header">Advanced US Freight Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# Enhanced sidebar with modern design
with st.sidebar:
    st.markdown("### Navigation & Controls")
    dashboard = st.radio(
        "Select Dashboard", 
        ("Rail Analytics", "Port Analytics", "Comparative Analysis"),
        help="Choose the analytics dashboard you want to explore"
    )
    
    st.markdown("---")
    st.markdown("### Analysis Options")
    analysis_type = st.selectbox(
        "Analysis Type",
        ["Overview", "Seasonal Analysis", "Trend Analysis"]
    )
    
    st.markdown("---")
    st.markdown("### Display Settings")
    show_raw_data = st.checkbox("Show Raw Data Tables", value=False)

# Load data
rail_df = load_rail_data()
port_df = load_port_data()

# Enhanced Rail Dashboard
if dashboard == "Rail Analytics":
    if not rail_df.empty:
        st.markdown('<h2 class="sub-header">Advanced Rail Freight Analytics</h2>', unsafe_allow_html=True)
        
        # Enhanced filters with better UX
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_years = st.multiselect(
                'Select Year(s)', 
                options=sorted(rail_df['Year'].unique()), 
                default=sorted(rail_df['Year'].unique()),
                help="Choose years for analysis"
            )
        
        with col2:
            selected_railroads = st.multiselect(
                'Select Railroad(s)', 
                options=sorted(rail_df['Railroad'].unique()), 
                default=sorted(rail_df['Railroad'].unique()),
                help="Choose railroad companies"
            )
        
        with col3:
            selected_commodities = st.multiselect(
                'Select Commodity(s)',
                options=sorted(rail_df['Commodity'].unique()),
                default=sorted(rail_df['Commodity'].unique())[:5],
                help="Choose commodity types"
            )
        
        # Filter data
        filtered_df = rail_df[
            (rail_df['Year'].isin(selected_years)) & 
            (rail_df['Railroad'].isin(selected_railroads)) &
            (rail_df['Commodity'].isin(selected_commodities))
        ]
        
        if not filtered_df.empty:
            # KPI Metrics
            st.markdown("### Key Performance Indicators")
            col1, col2, col3, col4 = st.columns(4)
            
            total_carloads = filtered_df['Carloads'].sum()
            avg_monthly = filtered_df.groupby(['Year', 'Month'])['Carloads'].sum().mean()
            peak_month = filtered_df.groupby('Month')['Carloads'].sum().idxmax()
            growth_rate = 0
            if len(selected_years) > 1:
                last_year = filtered_df[filtered_df['Year'] == max(selected_years)]['Carloads'].sum()
                first_year = filtered_df[filtered_df['Year'] == min(selected_years)]['Carloads'].sum()
                if first_year > 0:
                    growth_rate = ((last_year - first_year) / first_year) * 100
            
            create_metric_cards(
                col1, col2, col3, col4,
                "Total Carloads", f"{total_carloads:,.0f}",
                "Monthly Average", f"{avg_monthly:,.0f}",
                "Peak Month", f"Month {peak_month}",
                "Growth Rate", f"{growth_rate:.1f}%"
            )
            
            # Enhanced visualizations based on analysis type
            if analysis_type == "Overview":
                st.markdown("### Overview Analytics")
                
                # Time series analysis
                st.markdown("#### Railroad Performance Over Time")
                date_totals = filtered_df.groupby(['Date', 'Railroad'])['Carloads'].sum().reset_index()
                
                fig_trend = px.line(
                    date_totals,
                    x='Date',
                    y='Carloads',
                    color='Railroad',
                    title='Railroad Carloads Over Time',
                    markers=True
                )
                fig_trend.update_layout(height=600)
                st.plotly_chart(fig_trend, use_container_width=True)
                
                # Interactive heatmap
                st.markdown("#### Monthly Performance Heatmap")
                pivot_data = filtered_df.pivot_table(
                    values='Carloads', 
                    index='Month', 
                    columns='Railroad', 
                    aggfunc='sum'
                ).fillna(0)
                
                fig_heatmap = px.imshow(
                    pivot_data.values,
                    x=pivot_data.columns,
                    y=pivot_data.index,
                    title='Monthly Carloads Heatmap by Railroad',
                    color_continuous_scale='Viridis',
                    aspect='auto'
                )
                fig_heatmap.update_layout(height=500)
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
            elif analysis_type == "Seasonal Analysis":
                st.markdown("### Advanced Seasonal Analysis")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Seasonal patterns by commodity
                    seasonal_commodity = filtered_df.groupby(['Season', 'Commodity'])['Carloads'].sum().reset_index()
                    fig_seasonal = px.sunburst(
                        seasonal_commodity,
                        path=['Season', 'Commodity'],
                        values='Carloads',
                        title="Seasonal Distribution by Commodity",
                        color='Carloads',
                        color_continuous_scale='Viridis'
                    )
                    fig_seasonal.update_layout(height=500)
                    st.plotly_chart(fig_seasonal, use_container_width=True)
                
                with col2:
                    # Seasonal comparison across years
                    yearly_seasonal = filtered_df.groupby(['Year', 'Season'])['Carloads'].sum().reset_index()
                    fig_yearly = px.bar(
                        yearly_seasonal,
                        x='Year',
                        y='Carloads',
                        color='Season',
                        title="Seasonal Patterns Across Years",
                        barmode='group'
                    )
                    fig_yearly.update_layout(height=500)
                    st.plotly_chart(fig_yearly, use_container_width=True)
                
                # Statistical insights
                st.markdown("#### Seasonal Statistics")
                seasonal_stats = filtered_df.groupby('Season')['Carloads'].agg(['mean', 'std', 'min', 'max']).round(0)
                seasonal_stats.columns = ['Average', 'Std Dev', 'Minimum', 'Maximum']
                st.dataframe(seasonal_stats, use_container_width=True)
                
            elif analysis_type == "Trend Analysis":
                st.markdown("### Trend Analysis")
                
                # Year-over-year growth analysis
                yearly_totals = filtered_df.groupby(['Year', 'Railroad'])['Carloads'].sum().reset_index()
                
                # Calculate growth rates
                growth_data = []
                for railroad in yearly_totals['Railroad'].unique():
                    railroad_data = yearly_totals[yearly_totals['Railroad'] == railroad].sort_values('Year')
                    railroad_data['Growth_Rate'] = railroad_data['Carloads'].pct_change() * 100
                    growth_data.append(railroad_data)
                
                if growth_data:
                    growth_df = pd.concat(growth_data)
                    
                    fig_growth = px.line(
                        growth_df.dropna(),
                        x='Year',
                        y='Growth_Rate',
                        color='Railroad',
                        title='Year-over-Year Growth Rates by Railroad',
                        markers=True
                    )
                    fig_growth.add_hline(y=0, line_dash="dash", line_color="red")
                    fig_growth.update_layout(yaxis_title="Growth Rate (%)", height=500)
                    st.plotly_chart(fig_growth, use_container_width=True)
            
            # Raw data display option
            if show_raw_data:
                st.markdown("### Raw Data Sample")
                st.dataframe(filtered_df.sample(min(1000, len(filtered_df))))
                
        else:
            st.warning("No data available for the selected filters. Please adjust your selection.")
    else:
        st.error("Unable to load rail data. Please check the data file.")

# Enhanced Port Dashboard
elif dashboard == "Port Analytics":
    if not port_df.empty:
        st.markdown('<h2 class="sub-header">Advanced Port Container Analytics</h2>', unsafe_allow_html=True)
        
        # Enhanced filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_years = st.multiselect(
                'Select Year(s)', 
                options=sorted(port_df['year'].unique()), 
                default=sorted(port_df['year'].unique()),
                help="Choose years for analysis"
            )
        
        with col2:
            selected_months = st.multiselect(
                'Select Month(s)', 
                options=port_df['month'].unique(), 
                default=port_df['month'].unique(),
                help="Choose months for analysis"
            )
        
        with col3:
            selected_ports = st.multiselect(
                'Select Port(s)', 
                options=sorted(port_df['port_name'].unique()), 
                default=sorted(port_df['port_name'].unique())[:3],
                help="Choose ports to analyze"
            )
        
        # Filter data
        filtered_df = port_df[
            (port_df['year'].isin(selected_years)) & 
            (port_df['month'].isin(selected_months)) &
            (port_df['port_name'].isin(selected_ports))
        ]
        
        if not filtered_df.empty:
            # KPI Metrics for ports
            st.markdown("### Port Performance KPIs")
            col1, col2, col3, col4 = st.columns(4)
            
            total_teu = filtered_df['TEU_values'].sum()
            avg_monthly = filtered_df.groupby(['year', 'month'])['TEU_values'].sum().mean()
            top_port = filtered_df.groupby('port_name')['TEU_values'].sum().idxmax()
            port_count = filtered_df['port_name'].nunique()
            
            create_metric_cards(
                col1, col2, col3, col4,
                "Total TEU", f"{total_teu:,.0f}",
                "Monthly Average", f"{avg_monthly:,.0f}",
                "Top Port", top_port.replace('_', ' ').title(),
                "Active Ports", f"{port_count}"
            )
            
            # Enhanced port location data
            port_locations = {
                "charleston_sc": {"lat": 32.7765, "lon": -79.9311, "region": "Southeast", "coast": "Atlantic"},
                "houston_tx": {"lat": 29.7633, "lon": -95.3633, "region": "Gulf", "coast": "Gulf"},
                "long_beach_ca": {"lat": 33.7542, "lon": -118.1967, "region": "West", "coast": "Pacific"},
                "los_angeles_ca": {"lat": 33.742, "lon": -118.2719, "region": "West", "coast": "Pacific"},
                "nwsa_seattle_tacoma_wa": {"lat": 47.6097, "lon": -122.3331, "region": "Northwest", "coast": "Pacific"},
                "oakland_ca": {"lat": 37.8044, "lon": -122.2712, "region": "West", "coast": "Pacific"},
                "port_of_ny_nj": {"lat": 40.6895, "lon": -74.0455, "region": "Northeast", "coast": "Atlantic"},
                "port_of_virginia_va": {"lat": 36.8508, "lon": -76.2859, "region": "Southeast", "coast": "Atlantic"},
                "savannah_ga": {"lat": 32.0809, "lon": -81.0912, "region": "Southeast", "coast": "Atlantic"}
            }
            
            if analysis_type == "Overview":
                st.markdown("### Port Overview Analytics")
                
                # Advanced interactive map
                st.markdown("#### Interactive Port Performance Map")
                port_summary = filtered_df.groupby('port_name')['TEU_values'].sum().reset_index()
                port_summary['lat'] = port_summary['port_name'].map(lambda x: port_locations[x]['lat'])
                port_summary['lon'] = port_summary['port_name'].map(lambda x: port_locations[x]['lon'])
                port_summary['region'] = port_summary['port_name'].map(lambda x: port_locations[x]['region'])
                port_summary['coast'] = port_summary['port_name'].map(lambda x: port_locations[x]['coast'])
                
                fig_map = px.scatter_mapbox(
                    port_summary,
                    lat="lat", lon="lon", 
                    size="TEU_values", 
                    color="coast",
                    hover_name="port_name",
                    hover_data={"TEU_values": ":,.0f", "region": True},
                    size_max=50,
                    zoom=3,
                    mapbox_style="open-street-map",
                    title="Port Container Volume Distribution",
                    height=600
                )
                st.plotly_chart(fig_map, use_container_width=True)
                
                # Time series comparison
                st.markdown("#### Port Performance Over Time")
                fig_timeseries = px.line(
                    filtered_df,
                    x='port',
                    y='TEU_values',
                    color='port_name',
                    title='Monthly Container Throughput Trends',
                    markers=True,
                    height=500
                )
                st.plotly_chart(fig_timeseries, use_container_width=True)
                
            elif analysis_type == "Seasonal Analysis":
                st.markdown("### Seasonal Port Analysis")
                
                # Seasonal performance by coast
                seasonal_coast = filtered_df.copy()
                seasonal_coast['coast'] = seasonal_coast['port_name'].map(lambda x: port_locations[x]['coast'])
                seasonal_summary = seasonal_coast.groupby(['season', 'coast'])['TEU_values'].sum().reset_index()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_seasonal = px.bar(
                        seasonal_summary,
                        x='season',
                        y='TEU_values',
                        color='coast',
                        title='Seasonal Performance by Coast',
                        barmode='group'
                    )
                    st.plotly_chart(fig_seasonal, use_container_width=True)
                
                with col2:
                    # Top performing ports
                    top_ports = filtered_df.groupby('port_name')['TEU_values'].sum().nlargest(5)
                    fig_top = px.bar(
                        x=top_ports.values,
                        y=[name.replace('_', ' ').title() for name in top_ports.index],
                        orientation='h',
                        title='Top 5 Performing Ports (Total TEU)'
                    )
                    st.plotly_chart(fig_top, use_container_width=True)
            
            # Raw data option
            if show_raw_data:
                st.markdown("### Raw Port Data Sample")
                st.dataframe(filtered_df.sample(min(500, len(filtered_df))))
                
        else:
            st.warning("No port data available for the selected filters.")
    else:
        st.error("Unable to load port data. Please check the data file.")

# Comparative Analysis Dashboard
elif dashboard == "Comparative Analysis":
    st.markdown('<h2 class="sub-header">Multi-Modal Freight Comparison</h2>', unsafe_allow_html=True)
    
    if not rail_df.empty and not port_df.empty:
        # Unified analysis
        st.markdown("### Rail vs Port Transportation Analysis")
        
        # Convert units for comparison
        conversion_factor = st.slider("Rail-to-TEU Conversion Factor", 1.0, 5.0, 2.5, 0.1,
                                     help="Approximate TEU equivalent per railcar")
        
        # Aggregate data by year
        rail_yearly = rail_df.groupby('Year')['Carloads'].sum() * conversion_factor
        port_yearly = port_df.groupby('year')['TEU_values'].sum()
        
        # Align years
        common_years = list(set(rail_yearly.index) & set(port_yearly.index))
        if common_years:
            rail_common = rail_yearly[common_years]
            port_common = port_yearly[common_years]
            
            comparison_df = pd.DataFrame({
                'Year': common_years,
                'Rail_TEU_Equivalent': rail_common.values,
                'Port_TEU': port_common.values
            })
            
            # Comparative visualization
            fig_comparison = go.Figure()
            
            fig_comparison.add_trace(go.Scatter(
                x=comparison_df['Year'],
                y=comparison_df['Rail_TEU_Equivalent'],
                mode='lines+markers',
                name='Rail (TEU Equivalent)',
                line=dict(color='blue', width=3)
            ))
            
            fig_comparison.add_trace(go.Scatter(
                x=comparison_df['Year'],
                y=comparison_df['Port_TEU'],
                mode='lines+markers',
                name='Port Container',
                line=dict(color='red', width=3)
            ))
            
            fig_comparison.update_layout(
                title='Multi-Modal Freight Volume Comparison',
                xaxis_title='Year',
                yaxis_title='Volume (TEU Equivalent)',
                height=500
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Key insights
            st.markdown("### Key Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div class="insight-box">
                    <h4>Rail Transportation</h4>
                    <ul>
                        <li>Handles bulk commodities efficiently</li>
                        <li>Long-distance inland transportation</li>
                        <li>Lower per-unit cost for heavy cargo</li>
                        <li>Weather-dependent seasonal variations</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="insight-box">
                    <h4>Port Transportation</h4>
                    <ul>
                        <li>International trade gateway</li>
                        <li>Containerized cargo specialization</li>
                        <li>Higher throughput capacity</li>
                        <li>Less weather sensitivity</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        st.error("Unable to load data for comparative analysis.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p><strong>Advanced US Freight Analytics Dashboard</strong></p>
    <p>Data Sources: USDA Agricultural Transportation | Port Authority Websites</p>
    <p>Enhanced by: Megh KC | Built with Streamlit & Advanced Analytics</p>
</div>
""", unsafe_allow_html=True)
