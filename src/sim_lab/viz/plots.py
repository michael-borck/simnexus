"""Visualization utilities for SimLab."""

import matplotlib.pyplot as plt
from typing import List, Optional, Tuple, Dict, Any
import numpy as np


def plot_time_series(
    data: List[float],
    title: str = "Simulation Results",
    xlabel: str = "Days",
    ylabel: str = "Value",
    figsize: Tuple[int, int] = (10, 6),
    show: bool = True,
    save_path: Optional[str] = None,
    events: Optional[Dict[int, str]] = None,
    **kwargs
) -> plt.Figure:
    """Plot time series data from a simulation.
    
    Args:
        data: List of values to plot
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        figsize: Figure size as (width, height) in inches
        show: Whether to display the plot
        save_path: Path to save the figure (if None, figure is not saved)
        events: Dictionary mapping days to event labels
        **kwargs: Additional keyword arguments passed to plt.plot()
        
    Returns:
        The matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the main time series
    ax.plot(data, **kwargs)
    
    # Add event markers if provided
    if events:
        for day, label in events.items():
            if 0 <= day < len(data):
                ax.axvline(x=day, linestyle='--', color='red', alpha=0.7)
                ax.text(day, max(data) * 0.95, label, rotation=90, 
                       verticalalignment='top', fontsize=9)
    
    # Set labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    
    # Add grid
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Tight layout
    fig.tight_layout()
    
    # Save figure if path is provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    # Show plot if requested
    if show:
        plt.show()
    
    return fig


def plot_comparison(
    data_sets: Dict[str, List[float]],
    title: str = "Simulation Comparison",
    xlabel: str = "Days",
    ylabel: str = "Value",
    figsize: Tuple[int, int] = (12, 6),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Plot multiple time series for comparison.
    
    Args:
        data_sets: Dictionary mapping labels to lists of values
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        figsize: Figure size as (width, height) in inches
        show: Whether to display the plot
        save_path: Path to save the figure (if None, figure is not saved)
        
    Returns:
        The matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot each data set
    for label, data in data_sets.items():
        ax.plot(data, label=label)
    
    # Set labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    
    # Add legend and grid
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Tight layout
    fig.tight_layout()
    
    # Save figure if path is provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    # Show plot if requested
    if show:
        plt.show()
    
    return fig


def plot_histogram(
    data: List[float],
    title: str = "Distribution of Results",
    xlabel: str = "Value",
    ylabel: str = "Frequency",
    bins: int = 20,
    figsize: Tuple[int, int] = (10, 6),
    show: bool = True,
    save_path: Optional[str] = None,
) -> plt.Figure:
    """Plot a histogram of simulation results.
    
    Args:
        data: List of values to plot
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        bins: Number of bins in the histogram
        figsize: Figure size as (width, height) in inches
        show: Whether to display the plot
        save_path: Path to save the figure (if None, figure is not saved)
        
    Returns:
        The matplotlib Figure object
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot histogram
    ax.hist(data, bins=bins, alpha=0.7, edgecolor='black')
    
    # Add mean and median lines
    mean_val = np.mean(data)
    median_val = np.median(data)
    ax.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.2f}')
    ax.axvline(median_val, color='green', linestyle='--', label=f'Median: {median_val:.2f}')
    
    # Set labels and title
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    
    # Add legend and grid
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # Tight layout
    fig.tight_layout()
    
    # Save figure if path is provided
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    
    # Show plot if requested
    if show:
        plt.show()
    
    return fig