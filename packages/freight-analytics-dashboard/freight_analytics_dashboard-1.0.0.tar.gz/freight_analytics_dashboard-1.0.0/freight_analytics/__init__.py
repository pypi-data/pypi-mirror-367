"""
US Freight Analytics Dashboard Package

A comprehensive freight transportation analytics platform providing interactive 
visualizations and insights for rail and port data across the United States.
"""

__version__ = "1.0.0"
__author__ = "Megh KC"
__email__ = "kc.megh2048@gmail.com"
__description__ = "Advanced US Freight Analytics Dashboard with Interactive Visualizations"

# Import main classes when available
try:
    from .dashboard import FreightDashboard
    __all__ = ["FreightDashboard"]
except ImportError:
    # Handle case where dependencies aren't installed yet
    __all__ = []
