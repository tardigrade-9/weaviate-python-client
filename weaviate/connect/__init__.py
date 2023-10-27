"""
Module communication to a Weaviate instance. Used to connect to
Weaviate and run REST requests.
"""

__all__ = ["Connection", "ConnectionAsync"]

from .asynchronous import ConnectionAsync
from .connection import Connection
