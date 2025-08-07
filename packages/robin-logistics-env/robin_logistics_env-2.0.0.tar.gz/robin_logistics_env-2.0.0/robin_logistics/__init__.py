"""
Robin Logistics Environment - Multi-Depot Vehicle Routing Optimization
A comprehensive logistics optimization environment for developing and testing
vehicle routing algorithms with real-world constraints and interactive visualization.
"""

__version__ = "2.0.0"
__author__ = "Robin Logistics Team"
__email__ = "info@robin-logistics.com"

from .environment import LogisticsEnvironment
from .exceptions import (
    LogisticsError,
    InvalidSolutionError,
    CapacityExceededError,
    RouteValidationError
)

__all__ = [
    "LogisticsEnvironment",
    "LogisticsError", 
    "InvalidSolutionError",
    "CapacityExceededError",
    "RouteValidationError"
]