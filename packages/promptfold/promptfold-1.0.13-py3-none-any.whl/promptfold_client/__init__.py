"""
PromptFold Client

Python client for the PromptFold API - compress prompts with PromptFold.
"""

__version__ = "1.0.12"

from .client import PromptFold, PromptFoldError, CompressionError
from .models import CompressionResult

__all__ = [
    "PromptFold",
    "PromptFoldError",
    "CompressionError",
    "CompressionResult"
]