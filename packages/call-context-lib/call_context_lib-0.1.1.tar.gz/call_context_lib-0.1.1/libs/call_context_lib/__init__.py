"""Call Context Library

A Python context management library for applications with callback support.
"""

from .base import BaseCallContext
from .core import CallContext, CallContextCallbackHandler

__version__ = "0.1.0"
__all__ = ["CallContext", "CallContextCallbackHandler", "BaseCallContext"]
