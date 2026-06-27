"""Configuration settings for SimLab."""

import os
from pathlib import Path
from typing import Dict, Any, Optional

# Define default settings
DEFAULT_SETTINGS = {
    # General settings
    "results_dir": os.path.expanduser("~/sim_lab_results"),
    
    # Stock market simulation defaults
    "stock_market": {
        "start_price": 100.0,
        "days": 365,
        "volatility": 0.02,
        "drift": 0.001,
        "event_day": None,
        "event_impact": 0.0,
    },
    
    # Resource fluctuations simulation defaults
    "resource_fluctuations": {
        "start_price": 100.0,
        "days": 365,
        "volatility": 0.02,
        "drift": 0.001,
        "disruption_day": None,
        "disruption_severity": 0.0,
    },
    
    # Product popularity simulation defaults
    "product_popularity": {
        "days": 365,
        "initial_popularity": 0.01,
        "virality_factor": 0.1,
        "marketing_effectiveness": 0.05,
    },
    
    # Visualization settings
    "visualization": {
        "default_figsize": (10, 6),
        "dpi": 300,
        "style": "default"  # Can also be "ggplot", "seaborn", etc.
    }
}


def get_settings() -> Dict[str, Any]:
    """Get the current settings.
    
    Returns:
        Dictionary containing all settings
    """
    return DEFAULT_SETTINGS


def get_results_dir() -> str:
    """Get the results directory path.
    
    Returns:
        Path to the directory for storing simulation results
    """
    results_dir = DEFAULT_SETTINGS["results_dir"]
    
    # Create directory if it doesn't exist
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    return results_dir


def get_simulation_defaults(simulation_type: str) -> Dict[str, Any]:
    """Get default settings for a specific simulation type.
    
    Args:
        simulation_type: Name of the simulation type
        
    Returns:
        Dictionary of default settings for the specified simulation
        
    Raises:
        ValueError: If the simulation type is not recognized
    """
    if simulation_type in DEFAULT_SETTINGS:
        return DEFAULT_SETTINGS[simulation_type]
    
    raise ValueError(f"Unknown simulation type: {simulation_type}")