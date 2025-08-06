"""Call Context Library

A Python context management library for applications with callback support.
"""

from .base import BaseCallContext
from .bind import bind
from .core import CallContext, CallContextCallback

__version__ = "0.1.0"
__all__ = ["CallContext", "CallContextCallback", "BaseCallContext", "bind"]
