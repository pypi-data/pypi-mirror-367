"""Test suite for freight analytics package."""

import pytest
import pandas as pd
from freight_analytics import FreightDashboard


def test_dashboard_initialization():
    """Test dashboard can be initialized."""
    dashboard = FreightDashboard()
    assert dashboard is not None


def test_load_rail_data():
    """Test rail data loading."""
    dashboard = FreightDashboard()
    rail_data = dashboard.load_rail_data()
    
    assert isinstance(rail_data, pd.DataFrame)
    assert not rail_data.empty
    assert 'Carloads' in rail_data.columns
    assert 'Date' in rail_data.columns


def test_load_port_data():
    """Test port data loading."""
    dashboard = FreightDashboard()
    port_data = dashboard.load_port_data()
    
    assert isinstance(port_data, pd.DataFrame)
    assert not port_data.empty
    assert 'TEU_values' in port_data.columns


def test_rail_summary():
    """Test rail data summary."""
    dashboard = FreightDashboard()
    summary = dashboard.get_rail_summary()
    
    assert 'total_records' in summary
    assert 'total_carloads' in summary
    assert summary['total_records'] > 0


def test_port_summary():
    """Test port data summary."""
    dashboard = FreightDashboard()
    summary = dashboard.get_port_summary()
    
    assert 'total_records' in summary
    assert 'total_teu' in summary
    assert summary['total_records'] > 0


def test_seasonal_analysis():
    """Test seasonal analysis functionality."""
    dashboard = FreightDashboard()
    
    rail_seasonal = dashboard.get_seasonal_analysis('rail')
    assert isinstance(rail_seasonal, dict)
    
    port_seasonal = dashboard.get_seasonal_analysis('port')
    assert isinstance(port_seasonal, dict)
