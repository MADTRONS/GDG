"""
Groq LLM Provider Adapter.

This module provides an implementation of the LLMProvider interface for Groq's API.
"""

import time
from typing import Optional

from groq import Groq, APIError, RateLimitError as GroqRateLimitError, APITimeoutError, AuthenticationError

from .base import LLMProvider, LLMResponse, ProviderError, RateLimitError, InvalidKeyError, TimeoutError


class GroqAdapter(LLMProvider):
    """
    Adapter for Groq's LLM API.
    
    Groq provides fast inference with OpenAI-compatible API format.
    Default model: llama-3.3-70b-versatile (high quality, good speed)
    """
    
    DEFAULT_MODEL = "llama-3.3-70b-versatile"
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize the Groq adapter.
        
        Args:
            api_key: Groq API key
            model: Model name to use (defaults to llama-3.3-70b-versatile)
        """
        super().__init__(api_key)
        self.model = model or self.DEFAULT_MODEL
        try:
            self.client = Groq(api_key=api_key)
        except Exception as e:
            raise InvalidKeyError(f"Failed to initialize Groq client: {str(e)}")
    
    @property
    def name(self) -> str:
        """Return the provider name."""
        return "groq"
    
    def generate(
        self,
        prompt: str,
        system_message: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> LLMResponse:
        """
        Generate a response using Groq's API.
        
        Args:
            prompt: The user's input prompt
            system_message: System message defining the assistant's role
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLMResponse with the generated content and metadata
            
        Raises:
            RateLimitError: When rate limit is exceeded
            TimeoutError: When request times out
            InvalidKeyError: When API key is invalid
            ProviderError: For other API errors
        """
        start_time = time.time()
        
        try:
            # Make API call to Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response data
            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            return LLMResponse(
                content=content,
                provider_name=self.name,
                tokens_used=tokens_used,
                latency_ms=latency_ms
            )
            
        except AuthenticationError as e:
            raise InvalidKeyError(f"Groq authentication failed: {str(e)}")
        
        except GroqRateLimitError as e:
            raise RateLimitError(f"Groq rate limit exceeded: {str(e)}")
        
        except APITimeoutError as e:
            raise TimeoutError(f"Groq request timed out: {str(e)}")
        
        except APIError as e:
            raise ProviderError(f"Groq API error: {str(e)}")
        
        except Exception as e:
            raise ProviderError(f"Unexpected error with Groq: {str(e)}")
