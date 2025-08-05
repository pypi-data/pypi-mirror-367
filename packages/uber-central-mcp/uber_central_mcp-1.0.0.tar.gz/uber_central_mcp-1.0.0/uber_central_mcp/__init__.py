"""
Uber Central MCP Server

This package provides a Model Context Protocol (MCP) server for accessing
the Uber Central API functionality through natural language interactions.
"""

__version__ = "1.0.0"
__author__ = "Uber Central Team"

from .server import main

__all__ = ["main"]