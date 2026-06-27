"""Validation utilities for SimLab."""

from typing import Any, Optional, Tuple, List, Dict, Callable


def validate_range(
    value: float,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    name: str = "value"
) -> None:
    """Validate that a value is within a specified range.
    
    Args:
        value: The value to validate
        min_value: Minimum acceptable value (inclusive)
        max_value: Maximum acceptable value (inclusive)
        name: Name of the parameter for error messages
        
    Raises:
        ValueError: If value is outside the specified range
    """
    if min_value is not None and value < min_value:
        raise ValueError(f"{name} must be at least {min_value}")
    
    if max_value is not None and value > max_value:
        raise ValueError(f"{name} must not exceed {max_value}")


def validate_positive(value: float, name: str = "value") -> None:
    """Validate that a value is positive.
    
    Args:
        value: The value to validate
        name: Name of the parameter for error messages
        
    Raises:
        ValueError: If value is not positive
    """
    if value <= 0:
        raise ValueError(f"{name} must be positive")


def validate_non_negative(value: float, name: str = "value") -> None:
    """Validate that a value is non-negative.
    
    Args:
        value: The value to validate
        name: Name of the parameter for error messages
        
    Raises:
        ValueError: If value is negative
    """
    if value < 0:
        raise ValueError(f"{name} must be non-negative")


def validate_probability(value: float, name: str = "value") -> None:
    """Validate that a value is a valid probability (between 0 and 1).
    
    Args:
        value: The value to validate
        name: Name of the parameter for error messages
        
    Raises:
        ValueError: If value is not between 0 and 1
    """
    validate_range(value, 0, 1, name)


def validate_day(day: int, max_days: int, name: str = "day") -> None:
    """Validate that a day value is within the simulation period.
    
    Args:
        day: The day value to validate
        max_days: The maximum number of days in the simulation
        name: Name of the parameter for error messages
        
    Raises:
        ValueError: If day is not within the valid range
    """
    validate_range(day, 0, max_days - 1, name)