"""Exception classes for the Robin Logistics Environment."""


class LogisticsError(Exception):
    """Base exception for all logistics-related errors."""
    pass


class InvalidSolutionError(LogisticsError):
    """Raised when a solution violates problem constraints."""
    pass


class CapacityExceededError(LogisticsError):
    """Raised when vehicle capacity limits are exceeded."""
    pass


class RouteValidationError(LogisticsError):
    """Raised when route structure is invalid."""
    pass


class InventoryError(LogisticsError):
    """Raised when inventory constraints are violated."""
    pass