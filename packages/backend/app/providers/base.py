"""
Base abstraction for LLM providers.

This module defines the abstract base class for LLM providers and the common
response format used across all providers in the system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


# Exception classes
class ProviderError(Exception):
    """Base exception for provider-related errors."""
    pass


class RateLimitError(ProviderError):
    """Raised when the provider's rate limit is exceeded."""
    pass


class InvalidKeyError(ProviderError):
    """Raised when the API key is invalid or missing."""
    pass


class TimeoutError(ProviderError):
    """Raised when the provider request times out."""
    pass


# Response data class
@dataclass
class LLMResponse:
    """
    Standardized response format from all LLM providers.
    
    Attributes:
        content: The generated text response
        provider_name: Name of the provider that generated the response
        tokens_used: Number of tokens consumed (input + output)
        latency_ms: Response latency in milliseconds
    """
    content: str
    provider_name: str
    tokens_used: int
    latency_ms: float


# Abstract base class
class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All provider implementations must inherit from this class and implement
    the generate() method.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the provider with an API key.
        
        Args:
            api_key: The API key for the provider
            
        Raises:
            InvalidKeyError: If the API key is missing or empty
        """
        if not api_key:
            raise InvalidKeyError(f"API key is required for {self.__class__.__name__}")
        self.api_key = api_key
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_message: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: The user's input prompt
            system_message: System message defining the assistant's role
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLMResponse with the generated content and metadata
            
        Raises:
            ProviderError: For general provider errors
            RateLimitError: When rate limit is exceeded
            TimeoutError: When request times out
            InvalidKeyError: When API key is invalid
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this provider."""
        pass
