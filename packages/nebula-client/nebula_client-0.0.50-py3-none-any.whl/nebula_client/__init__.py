"""
Nebula Client SDK - A clean, intuitive SDK for Nebula Cloud API

This SDK provides a simplified interface to Nebula's memory and retrieval capabilities,
focusing on chunks and hiding the complexity of the underlying R2R system.
"""

from .client import NebulaClient
from .exceptions import (
    NebulaException, 
    NebulaClientException,
    NebulaAuthenticationException,
    NebulaRateLimitException,
    NebulaValidationException
)
from .models import Memory, Cluster, SearchResult, RetrievalType

__version__ = "0.0.50"
__all__ = [
    "NebulaClient",
    "NebulaException", 
    "NebulaClientException",
    "NebulaAuthenticationException",
    "NebulaRateLimitException",
    "NebulaValidationException",
    "Memory",
    "Cluster",
    "SearchResult", 
    "RetrievalType"
] 