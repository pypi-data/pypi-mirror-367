"""
PromptFold Data Models

This module defines the data structures for prompt compression requests and responses.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CompressionResult:
    """Result of prompt compression with compressed system and user prompts"""
    compressed_system_prompt: str
    compressed_user_prompt: str
    input_system_prompt: str
    input_user_prompt: str
    improvement_score: Optional[float] = None