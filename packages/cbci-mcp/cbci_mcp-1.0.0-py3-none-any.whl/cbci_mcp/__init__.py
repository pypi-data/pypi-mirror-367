#!/usr/bin/env python3
"""
CBCI MCP (Model Context Protocol) Package
ChatBot CI - LLM-powered ChatBot with Dynamic Database Querying
"""

from .client import CBCIMCPClient
from .server import CBCIMCPServer

__version__ = "1.0.0"
__author__ = "CBCI MCP Team"
__email__ = "rosci671233@gmail.com"

__all__ = ["CBCIMCPClient", "CBCIMCPServer"] 