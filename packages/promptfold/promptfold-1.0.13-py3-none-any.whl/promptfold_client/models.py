"""
PromptFold Data Models

This module defines the data structures for prompt compression requests and responses.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CompressionResult:
    """
    Result of a prompt compression operation
    
    Attributes:
        compressed_user_prompt: The compressed version of the user prompt
        compressed_system_prompt: The compressed version of the system prompt (if provided)
        original_tokens: Number of tokens in the original prompt(s)
        compressed_tokens: Number of tokens in the compressed prompt(s)
        compression_ratio: Ratio showing compression efficiency (0.0 to 1.0)
        tokens_saved: Number of tokens saved through compression
    """
    compressed_user_prompt: str
    compressed_system_prompt: Optional[str] = None
    original_tokens: Optional[int] = None
    compressed_tokens: Optional[int] = None
    compression_ratio: Optional[float] = None
    tokens_saved: Optional[int] = None