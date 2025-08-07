"""
CNHK MCP Server

A Model Context Protocol (MCP) server for quantitative research and data analysis.
Provides comprehensive tools for research, simulation, and data analysis.
"""

__version__ = "1.0.4"
__author__ = "CNHK MCP"
__email__ = "support@example.com"

try:
    from .client import ApiClient
    from .server import CNHKMCPServer
    __all__ = ["ApiClient", "CNHKMCPServer"]
except ImportError:
    # Handle import errors gracefully during package building
    __all__ = []
