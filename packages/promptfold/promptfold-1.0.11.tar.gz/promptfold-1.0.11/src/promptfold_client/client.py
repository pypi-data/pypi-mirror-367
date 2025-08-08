"""
PromptFold API Client

This module provides a client for compressing prompts using the PromptFold API.
"""

import json
import logging
import requests
from typing import Optional, Dict, Any
from .models import CompressionResult

# Set up logger for the client
logger = logging.getLogger('promptfold_client')
logger.setLevel(logging.INFO)


class PromptFoldError(Exception):
    """Base exception for PromptFold client errors"""
    pass


class CompressionError(PromptFoldError):
    """Raised when prompt compression fails"""
    pass


class PromptFold:
    """Client for compressing prompts using the PromptFold API"""

    def __init__(self, api_key: str):
        """
        Initialize the PromptFold Client
        
        Args:
            api_key: API key for authentication (required)
        """
        if not api_key:
            raise ValueError("API key is required. Get your API key from https://promptfold.com")
        
        self.base_url = "https://promptfold-backend-581010343107.us-central1.run.app"
        self.api_key = api_key
        self.session = requests.Session()
        
        # Set up authentication headers
        self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        
        # Set default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'promptfold-client/1.0.10'
        })

    def compress(self, prompt: str) -> str:
        """
        Compress a prompt using the PromptFold API
        
        Args:
            prompt: The prompt text to compress
            
        Returns:
            str: The compressed prompt text
            
        Raises:
            CompressionError: If the compression fails
        """
        return self._compress_single_prompt(prompt)

    def _compress_single_prompt(self, prompt: str) -> str:
        """
        Internal method to compress a single prompt via the API
        
        Args:
            prompt: The prompt text to compress
            
        Returns:
            str: The compressed prompt text
            
        Raises:
            CompressionError: If the compression fails
        """
        try:
            # Make the API request
            url = f"{self.base_url}/compress"
            payload = {"prompt": prompt}
            
            response = self.session.post(url, json=payload)
            
            # Handle different response codes
            if response.status_code == 400:
                error_data = response.json() if response.content else {}
                raise CompressionError(f"Invalid request: {error_data.get('error', response.text)}")
            elif response.status_code == 401:
                raise CompressionError("Authentication failed - check your API key")
            elif response.status_code == 429:
                raise CompressionError("Rate limit exceeded - please try again later")
            elif response.status_code != 200:
                raise CompressionError(f"API request failed with status {response.status_code}: {response.text}")
            
            # Parse the response
            data = response.json()
            compressed_prompt = data['compressed_prompt']
            
            # Log compression stats if available
            original_tokens = data.get('original_tokens', 0)
            compressed_tokens = data.get('compressed_tokens', 0)
            compression_ratio = data.get('compression_ratio', 0)
            
            if original_tokens and compressed_tokens:
                tokens_saved = original_tokens - compressed_tokens
                logger.info(f"Compression successful: {original_tokens} → {compressed_tokens} tokens "
                           f"({compression_ratio:.1%} compression, {tokens_saved} tokens saved)")
            else:
                logger.info("Compression successful")
            
            return compressed_prompt
            
        except requests.RequestException as e:
            raise CompressionError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise CompressionError(f"Invalid JSON response: {str(e)}")


    def health_check(self) -> Dict[str, Any]:
        """
        Check API health status
        
        Returns:
            Dict containing health status information
            
        Raises:
            SemanticEQError: If health check fails
        """
        try:
            url = f"{self.base_url}/health"
            response = self.session.get(url)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise PromptFoldError(f"Health check failed with status {response.status_code}")
                
        except requests.RequestException as e:
            raise PromptFoldError(f"Health check network error: {str(e)}")