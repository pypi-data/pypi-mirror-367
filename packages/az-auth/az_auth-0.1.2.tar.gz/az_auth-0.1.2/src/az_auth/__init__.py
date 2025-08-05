"""
Azure authentication utilities for Microsoft Graph and ARM APIs.
"""

from .auth import AuthClientBase, AuthClientGraph, AuthClientARM

__version__ = "0.1.0"
__all__ = ["AuthClientBase", "AuthClientGraph", "AuthClientARM"]