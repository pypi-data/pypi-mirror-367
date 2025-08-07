"""
Exceptions for BRAIN MCP server.
"""


class BrainMCPError(Exception):
    """Base exception for BRAIN MCP server."""
    pass


class AuthenticationError(BrainMCPError):
    """Authentication failed."""
    pass


class SimulationError(BrainMCPError):
    """Simulation operation failed."""
    pass


class APIError(BrainMCPError):
    """API request failed."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class ValidationError(BrainMCPError):
    """Data validation failed."""
    pass


class ConfigurationError(BrainMCPError):
    """Configuration error."""
    pass


class TimeoutError(BrainMCPError):
    """Operation timed out."""
    pass
