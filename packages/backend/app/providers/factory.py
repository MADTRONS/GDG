"""
LLM Provider Factory.

This module provides a factory function to create the configured LLM provider
instance based on environment variables.
"""

import logging
from typing import Optional

from app.config import get_settings
from .base import LLMProvider
from .groq_adapter import GroqAdapter
from .gemini_adapter import GeminiAdapter

logger = logging.getLogger(__name__)

# Singleton instance cache
_provider_instance: Optional[LLMProvider] = None


class ProviderFactory:
    """
    Factory class for creating LLM provider instances.
    
    Reads the LLM_PROVIDER environment variable and returns the appropriate
    provider implementation. Implements singleton pattern to ensure one
    provider instance for the entire system.
    """
    
    @staticmethod
    def get_provider(force_new: bool = False) -> LLMProvider:
        """
        Get the configured LLM provider instance.
        
        This method reads the LLM_PROVIDER environment variable to determine
        which provider to instantiate. The provider instance is cached as a
        singleton for the lifetime of the application.
        
        Args:
            force_new: If True, creates a new instance even if one is cached
            
        Returns:
            LLMProvider instance (GroqAdapter or GeminiAdapter)
            
        Raises:
            ValueError: If required API key for the selected provider is missing
            
        Environment Variables:
            LLM_PROVIDER: "groq" or "gemini" (default: "gemini")
            GROQ_API_KEY: Required if using Groq
            GEMINI_API_KEY: Required if using Gemini
        """
        global _provider_instance
        
        # Return cached instance if available
        if _provider_instance is not None and not force_new:
            return _provider_instance
        
        settings = get_settings()
        provider_name = settings.llm_provider.lower().strip()
        
        logger.info(f"Initializing LLM provider: {provider_name}")
        
        if provider_name == "groq":
            if not settings.groq_api_key:
                logger.error("GROQ_API_KEY environment variable is not set")
                raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER=groq")
            
            _provider_instance = GroqAdapter(api_key=settings.groq_api_key)
            logger.info(f"✓ Groq provider initialized (model: {_provider_instance.model})")
            
        elif provider_name == "gemini":
            if not settings.gemini_api_key:
                logger.error("GEMINI_API_KEY environment variable is not set")
                raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER=gemini")
            
            _provider_instance = GeminiAdapter(api_key=settings.gemini_api_key)
            logger.info(f"✓ Gemini provider initialized (model: {_provider_instance.model_name})")
            
        else:
            logger.warning(
                f"Unknown LLM provider '{provider_name}', defaulting to 'gemini'. "
                f"Valid options: 'groq', 'gemini'"
            )
            
            if not settings.gemini_api_key:
                logger.error("GEMINI_API_KEY environment variable is not set (fallback)")
                raise ValueError("GEMINI_API_KEY is required for default provider")
            
            _provider_instance = GeminiAdapter(api_key=settings.gemini_api_key)
            logger.info(f"✓ Gemini provider initialized as fallback (model: {_provider_instance.model_name})")
        
        return _provider_instance
    
    @staticmethod
    def reset_provider() -> None:
        """
        Reset the cached provider instance.
        
        Useful for testing or when configuration changes require a new provider.
        """
        global _provider_instance
        _provider_instance = None
        logger.info("Provider instance cache cleared")


def get_llm_provider() -> LLMProvider:
    """
    Convenience function to get the configured LLM provider.
    
    This is the primary function that should be used throughout the application
    to obtain the LLM provider instance.
    
    Returns:
        LLMProvider instance configured via environment variables
    """
    return ProviderFactory.get_provider()
