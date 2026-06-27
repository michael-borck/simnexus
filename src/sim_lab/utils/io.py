"""Input/output utilities for SimLab."""

import os
import csv
import json
from typing import List, Dict, Any, Union


def save_to_csv(data: List[float], filepath: str, column_name: str = "value") -> None:
    """Save simulation data to a CSV file.
    
    Args:
        data: List of simulation values
        filepath: Path to save the CSV file
        column_name: Name of the data column
    """
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['day', column_name])
        for i, value in enumerate(data):
            writer.writerow([i, value])


def save_to_json(data: Dict[str, Any], filepath: str) -> None:
    """Save simulation data to a JSON file.
    
    Args:
        data: Dictionary containing simulation data and metadata
        filepath: Path to save the JSON file
    """
    with open(filepath, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=2)


def load_from_csv(filepath: str, value_column: str = "value") -> List[float]:
    """Load simulation data from a CSV file.
    
    Args:
        filepath: Path to the CSV file
        value_column: Name of the column containing the values
        
    Returns:
        List of values from the specified column
    """
    values = []
    with open(filepath, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            values.append(float(row[value_column]))
    return values


def load_from_json(filepath: str) -> Dict[str, Any]:
    """Load simulation data from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Dictionary containing the loaded data
    """
    with open(filepath, 'r') as jsonfile:
        return json.load(jsonfile)


def ensure_directory_exists(filepath: str) -> None:
    """Ensure that the directory for the given filepath exists.
    
    Args:
        filepath: Path to a file
    """
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)