# 📦 Package Usage Guide

## 🚀 **Installation & Quick Start**

### **Install Package**
```bash
pip install freight-analytics-dashboard
```

### **Launch Dashboard**
```bash
# Simple launch on default port (8501)
freight-dashboard

# Custom port
freight-dashboard --port 8502

# Network accessible
freight-dashboard --host 0.0.0.0 --port 8502

# Demo mode (if you want to test without full data)
freight-dashboard --demo
```

## 🐍 **Python API Usage**

### **Basic Usage**
```python
from freight_analytics import FreightDashboard

# Initialize dashboard
dashboard = FreightDashboard()

# Get data summaries
rail_summary = dashboard.get_rail_summary()
port_summary = dashboard.get_port_summary()

print("Rail Data:", rail_summary)
print("Port Data:", port_summary)
```

### **Working with Data**
```python
from freight_analytics import FreightDashboard

dashboard = FreightDashboard()

# Load raw data
rail_data = dashboard.load_rail_data()
port_data = dashboard.load_port_data()

# Get specific year data
rail_2023 = dashboard.get_rail_by_year(2023)
port_2023 = dashboard.get_port_by_year(2023)

# Seasonal analysis
rail_seasons = dashboard.get_seasonal_analysis('rail')
port_seasons = dashboard.get_seasonal_analysis('port')
```

### **Integration Example**
```python
import pandas as pd
from freight_analytics import FreightDashboard

def analyze_freight_trends():
    """Example analysis function."""
    dashboard = FreightDashboard()
    
    # Get summaries
    rail_summary = dashboard.get_rail_summary()
    port_summary = dashboard.get_port_summary()
    
    # Compare total volumes
    total_carloads = rail_summary['total_carloads']
    total_teu = port_summary['total_teu']
    
    print(f"Rail: {total_carloads:,} carloads")
    print(f"Port: {total_teu:,} TEU")
    
    # Get seasonal patterns
    rail_seasonal = dashboard.get_seasonal_analysis('rail')
    
    return {
        'rail': rail_summary,
        'port': port_summary,
        'seasonal': rail_seasonal
    }

# Run analysis
results = analyze_freight_trends()
```

## 🌐 **Web Dashboard Features**

When you run `freight-dashboard`, you get:

### **Rail Analytics**
- Overview with trend analysis and heatmaps
- Seasonal analysis with sunburst charts
- Trend analysis with growth rates
- Interactive filtering by year, railroad, commodity

### **Port Analytics**  
- Geographic performance mapping
- Time series comparisons
- Seasonal coast-wise analysis
- Port ranking and performance trends

### **Comparative Analysis**
- Multi-modal freight comparison
- Rail vs Port volume analysis
- TEU conversion capabilities
- Strategic insights

## ⚙️ **Configuration Options**

### **Environment Variables**
```bash
# Enable demo mode
export FREIGHT_DEMO_MODE=1
freight-dashboard

# Custom data directory (if you have your own data)
export FREIGHT_DATA_DIR=/path/to/your/data
freight-dashboard
```

### **Programmatic Configuration**
```python
from freight_analytics import FreightDashboard

# Use custom data directory
dashboard = FreightDashboard(data_dir="/path/to/custom/data")

# The data directory should contain:
# - Rail_Carloadings_originated.csv
# - port_dataset.json
```

## 🔧 **Development Setup**

### **Install in Development Mode**
```bash
git clone https://github.com/meghkc/DashBoard.git
cd DashBoard
pip install -e .
```

### **Run Tests**
```bash
pip install pytest
pytest tests/
```

### **Build Package**
```bash
pip install build
python -m build
```

## 🚀 **Advanced Usage**

### **Custom Data Processing**
```python
from freight_analytics import FreightDashboard
import plotly.express as px

dashboard = FreightDashboard()
rail_data = dashboard.load_rail_data()

# Create custom visualization
fig = px.line(
    rail_data.groupby(['Date', 'Railroad'])['Carloads'].sum().reset_index(),
    x='Date', 
    y='Carloads', 
    color='Railroad',
    title='Custom Rail Analysis'
)
fig.show()
```

### **Export Data**
```python
dashboard = FreightDashboard()

# Export to CSV
rail_data = dashboard.load_rail_data()
rail_data.to_csv('my_rail_analysis.csv', index=False)

# Export specific analysis
seasonal_data = dashboard.get_seasonal_analysis('rail')
import json
with open('seasonal_analysis.json', 'w') as f:
    json.dump(seasonal_data, f, indent=2)
```

## 📞 **Support**

- **Documentation**: [GitHub README](https://github.com/meghkc/DashBoard)
- **Issues**: [GitHub Issues](https://github.com/meghkc/DashBoard/issues)
- **Live Demo**: [Streamlit Cloud](https://meghkc-dashboard-freight-analysis.streamlit.app/)

---

**Happy analyzing! 🚛📊**
