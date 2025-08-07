"""Main FreightDashboard class for programmatic use."""

import pandas as pd
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class FreightDashboard:
    """
    Freight Analytics Dashboard for programmatic use.
    
    This class provides access to freight analytics data and basic processing
    functions that can be used in other Python applications.
    """
    
    def __init__(self, data_dir=None):
        """
        Initialize the FreightDashboard.
        
        Args:
            data_dir (str, optional): Path to data directory. 
                                    If None, uses package data.
        """
        if data_dir is None:
            self.data_dir = Path(__file__).parent / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self._rail_data = None
        self._port_data = None
    
    def load_rail_data(self):
        """Load and return rail freight data."""
        if self._rail_data is None:
            rail_file = self.data_dir / "Rail_Carloadings_originated.csv"
            if rail_file.exists():
                self._rail_data = pd.read_csv(rail_file)
                self._rail_data['Date'] = pd.to_datetime(self._rail_data['Date'])
                self._rail_data['Season'] = self._rail_data['Month'].apply(self._get_season)
            else:
                raise FileNotFoundError(f"Rail data file not found: {rail_file}")
        
        return self._rail_data.copy()
    
    def load_port_data(self):
        """Load and return port container data."""
        if self._port_data is None:
            port_file = self.data_dir / "port_dataset.json"
            if port_file.exists():
                with open(port_file, 'r') as f:
                    data = json.load(f)
                
                df = pd.DataFrame(data)
                df_melted = df.melt(id_vars=["port"], var_name="port_name", value_name="TEU_values")
                df_melted['port'] = pd.to_datetime(df_melted['port'], errors='coerce')
                df_melted['TEU_values'] = pd.to_numeric(df_melted['TEU_values'], errors='coerce')
                df_melted = df_melted.dropna(subset=['TEU_values'])
                df_melted['month'] = df_melted['port'].dt.strftime('%b')
                df_melted['year'] = df_melted['port'].dt.year
                df_melted['season'] = df_melted['month'].apply(self._get_season_water)
                
                self._port_data = df_melted
            else:
                raise FileNotFoundError(f"Port data file not found: {port_file}")
        
        return self._port_data.copy()
    
    def get_rail_summary(self):
        """Get summary statistics for rail data."""
        rail_df = self.load_rail_data()
        
        return {
            'total_records': len(rail_df),
            'date_range': {
                'start': rail_df['Date'].min().strftime('%Y-%m-%d'),
                'end': rail_df['Date'].max().strftime('%Y-%m-%d')
            },
            'total_carloads': rail_df['Carloads'].sum(),
            'unique_railroads': rail_df['Railroad'].nunique(),
            'unique_commodities': rail_df['Commodity'].nunique(),
            'years_covered': sorted(rail_df['Year'].unique().tolist())
        }
    
    def get_port_summary(self):
        """Get summary statistics for port data."""
        port_df = self.load_port_data()
        
        return {
            'total_records': len(port_df),
            'date_range': {
                'start': port_df['port'].min().strftime('%Y-%m-%d'),
                'end': port_df['port'].max().strftime('%Y-%m-%d')
            },
            'total_teu': port_df['TEU_values'].sum(),
            'unique_ports': port_df['port_name'].nunique(),
            'years_covered': sorted(port_df['year'].unique().tolist()),
            'ports': sorted(port_df['port_name'].unique().tolist())
        }
    
    def get_rail_by_year(self, year):
        """Get rail data for a specific year."""
        rail_df = self.load_rail_data()
        return rail_df[rail_df['Year'] == year].copy()
    
    def get_port_by_year(self, year):
        """Get port data for a specific year."""
        port_df = self.load_port_data()
        return port_df[port_df['year'] == year].copy()
    
    def get_seasonal_analysis(self, mode='rail'):
        """
        Get seasonal analysis for rail or port data.
        
        Args:
            mode (str): 'rail' or 'port'
            
        Returns:
            dict: Seasonal statistics
        """
        if mode == 'rail':
            df = self.load_rail_data()
            groupby_col = 'Carloads'
        elif mode == 'port':
            df = self.load_port_data()
            groupby_col = 'TEU_values'
        else:
            raise ValueError("Mode must be 'rail' or 'port'")
        
        seasonal_stats = df.groupby('Season')[groupby_col].agg([
            'sum', 'mean', 'count', 'std'
        ]).round(2)
        
        return seasonal_stats.to_dict()
    
    def _get_season(self, month):
        """Determine season based on month for rail data."""
        if month in [12, 1, 2]:
            return 'Winter'
        elif month in [3, 4, 5]:
            return 'Spring'
        elif month in [6, 7, 8]:
            return 'Summer'
        elif month in [9, 10, 11]:
            return 'Fall'
    
    def _get_season_water(self, month):
        """Determine season based on month for water data."""
        if month in ['Dec', 'Jan', 'Feb']:
            return 'Winter'
        elif month in ['Mar', 'Apr', 'May']:
            return 'Spring'
        elif month in ['Jun', 'Jul', 'Aug']:
            return 'Summer'
        elif month in ['Sep', 'Oct', 'Nov']:
            return 'Fall'

# Example usage functions
def quick_rail_summary():
    """Quick function to get rail data summary."""
    dashboard = FreightDashboard()
    return dashboard.get_rail_summary()

def quick_port_summary():
    """Quick function to get port data summary."""
    dashboard = FreightDashboard()
    return dashboard.get_port_summary()
