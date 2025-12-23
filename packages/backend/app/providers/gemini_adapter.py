"""
Gemini LLM Provider Adapter.

This module provides an implementation of the LLMProvider interface for Google's Gemini API.
"""

import time
from typing import Optional

import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.api_core import exceptions as google_exceptions

from .base import LLMProvider, LLMResponse, ProviderError, RateLimitError, InvalidKeyError, TimeoutError


class GeminiAdapter(LLMProvider):
    """
    Adapter for Google's Gemini LLM API.
    
    Gemini is Google's flagship model with strong reasoning capabilities.
    Default model: gemini-2.0-flash-exp (fast and capable)
    """
    
    DEFAULT_MODEL = "gemini-2.0-flash-exp"
    
    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize the Gemini adapter.
        
        Args:
            api_key: Google Gemini API key
            model: Model name to use (defaults to gemini-2.0-flash-exp)
        """
        super().__init__(api_key)
        self.model_name = model or self.DEFAULT_MODEL
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(self.model_name)
        except Exception as e:
            raise InvalidKeyError(f"Failed to initialize Gemini client: {str(e)}")
    
    @property
    def name(self) -> str:
        """Return the provider name."""
        return "gemini"
    
    def generate(
        self,
        prompt: str,
        system_message: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> LLMResponse:
        """
        Generate a response using Gemini's API.
        
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
            ProviderError: For other API errors including safety filters
        """
        start_time = time.time()
        
        try:
            # Combine system message and prompt for Gemini
            full_prompt = f"{system_message}\n\nUser: {prompt}\n\nAssistant:"
            
            # Configure generation parameters
            generation_config = GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            # Make API call to Gemini
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response data
            content = response.text if response.text else ""
            
            # Gemini doesn't always provide token counts, estimate based on response
            tokens_used = self._estimate_tokens(system_message, prompt, content)
            
            return LLMResponse(
                content=content,
                provider_name=self.name,
                tokens_used=tokens_used,
                latency_ms=latency_ms
            )
            
        except google_exceptions.Unauthenticated as e:
            raise InvalidKeyError(f"Gemini authentication failed: {str(e)}")
        
        except google_exceptions.ResourceExhausted as e:
            raise RateLimitError(f"Gemini rate limit exceeded: {str(e)}")
        
        except google_exceptions.DeadlineExceeded as e:
            raise TimeoutError(f"Gemini request timed out: {str(e)}")
        
        except google_exceptions.GoogleAPIError as e:
            raise ProviderError(f"Gemini API error: {str(e)}")
        
        except ValueError as e:
            # Gemini raises ValueError for safety filter blocks
            if "safety" in str(e).lower() or "block" in str(e).lower():
                raise ProviderError(f"Gemini safety filter triggered: {str(e)}")
            raise ProviderError(f"Gemini error: {str(e)}")
        
        except AttributeError as e:
            # Can happen if response has no text due to safety filters
            if "text" in str(e).lower():
                raise ProviderError("Gemini response blocked by safety filters")
            raise ProviderError(f"Unexpected Gemini response format: {str(e)}")
        
        except Exception as e:
            raise ProviderError(f"Unexpected error with Gemini: {str(e)}")
    
    def _estimate_tokens(self, system_message: str, prompt: str, response: str) -> int:
        """
        Estimate token count for Gemini responses.
        
        Rough estimation: ~4 characters per token for English text.
        
        Args:
            system_message: The system message
            prompt: The user prompt
            response: The generated response
            
        Returns:
            Estimated token count
        """
        total_chars = len(system_message) + len(prompt) + len(response)
        return max(int(total_chars / 4), 1)
