"""Tests for the LLM provider factory."""

import pytest
from unittest.mock import patch, Mock

from app.providers.factory import ProviderFactory, get_llm_provider
from app.providers.groq_adapter import GroqAdapter
from app.providers.gemini_adapter import GeminiAdapter


class TestProviderFactory:
    """Tests for ProviderFactory."""
    
    def setup_method(self):
        """Reset provider cache before each test."""
        ProviderFactory.reset_provider()
    
    def teardown_method(self):
        """Clean up after each test."""
        ProviderFactory.reset_provider()
    
    def test_factory_returns_groq_provider(self):
        """Test that factory returns Groq provider when configured."""
        mock_settings = Mock()
        mock_settings.llm_provider = "groq"
        mock_settings.groq_api_key = "test_groq_key"
        
        with patch('app.providers.factory.get_settings', return_value=mock_settings):
            with patch('app.providers.factory.GroqAdapter') as mock_groq:
                mock_instance = Mock(spec=GroqAdapter)
                mock_instance.model = "llama-3.3-70b-versatile"
                mock_groq.return_value = mock_instance
                
                provider = ProviderFactory.get_provider()
                
                # Verify Groq was instantiated with correct key
                mock_groq.assert_called_once_with(api_key="test_groq_key")
    
    def test_factory_returns_gemini_provider(self):
        """Test that factory returns Gemini provider when configured."""
        mock_settings = Mock()
        mock_settings.llm_provider = "gemini"
        mock_settings.gemini_api_key = "test_gemini_key"
        
        with patch('app.providers.factory.get_settings', return_value=mock_settings):
            with patch('app.providers.factory.GeminiAdapter') as mock_gemini:
                mock_instance = Mock(spec=GeminiAdapter)
                mock_instance.model_name = "gemini-2.0-flash-exp"
                mock_gemini.return_value = mock_instance
                
                provider = ProviderFactory.get_provider()
                
                # Verify Gemini was instantiated with correct key
                mock_gemini.assert_called_once_with(api_key="test_gemini_key")
    
    def test_factory_defaults_to_gemini_on_invalid_provider(self):
        """Test that factory defaults to Gemini when provider name is invalid."""
        mock_settings = Mock()
        mock_settings.llm_provider = "invalid_provider"
        mock_settings.gemini_api_key = "test_gemini_key"
        
        with patch('app.providers.factory.get_settings', return_value=mock_settings):
            with patch('app.providers.factory.GeminiAdapter') as mock_gemini:
                mock_gemini.return_value = Mock(spec=GeminiAdapter, model_name="gemini-2.0-flash-exp")
                
                provider = ProviderFactory.get_provider()
                
                # Verify Gemini was instantiated as fallback
                mock_gemini.assert_called_once_with(api_key="test_gemini_key")
    
    def test_factory_raises_error_when_groq_key_missing(self):
        """Test that factory raises error when Groq is selected but API key is missing."""
        mock_settings = Mock()
        mock_settings.llm_provider = "groq"
        mock_settings.groq_api_key = ""
        
        with patch('app.providers.factory.get_settings', return_value=mock_settings):
            with pytest.raises(ValueError) as exc_info:
                ProviderFactory.get_provider()
            
            assert "GROQ_API_KEY is required" in str(exc_info.value)
    
    def test_factory_raises_error_when_gemini_key_missing(self):
        """Test that factory raises error when Gemini is selected but API key is missing."""
        mock_settings = Mock()
        mock_settings.llm_provider = "gemini"
        mock_settings.gemini_api_key = ""
        
        with patch('app.providers.factory.get_settings', return_value=mock_settings):
            with pytest.raises(ValueError) as exc_info:
                ProviderFactory.get_provider()
            
            assert "GEMINI_API_KEY is required" in str(exc_info.value)
    
    def test_factory_caches_provider_instance(self):
        """Test that factory returns cached provider instance on subsequent calls."""
        mock_settings = Mock()
        mock_settings.llm_provider = "gemini"
        mock_settings.gemini_api_key = "test_key"
        
        with patch('app.providers.factory.get_settings', return_value=mock_settings):
            with patch('app.providers.factory.GeminiAdapter') as mock_gemini:
                mock_instance = Mock(spec=GeminiAdapter, model_name="gemini-2.0-flash-exp")
                mock_gemini.return_value = mock_instance
                
                # First call creates instance
                provider1 = ProviderFactory.get_provider()
                
                # Second call should return same instance without creating new one
                provider2 = ProviderFactory.get_provider()
                
                # Verify adapter was only instantiated once
                assert mock_gemini.call_count == 1
                
                # Verify same instance returned
                assert provider1 is provider2
    
    def test_factory_force_new_creates_new_instance(self):
        """Test that force_new parameter creates new instance even if cached."""
        mock_settings = Mock()
        mock_settings.llm_provider = "gemini"
        mock_settings.gemini_api_key = "test_key"
        
        with patch('app.providers.factory.get_settings', return_value=mock_settings):
            with patch('app.providers.factory.GeminiAdapter') as mock_gemini:
                mock_gemini.side_effect = [
                    Mock(spec=GeminiAdapter, model_name="gemini-2.0-flash-exp"),
                    Mock(spec=GeminiAdapter, model_name="gemini-2.0-flash-exp")
                ]
                
                # First call creates instance
                provider1 = ProviderFactory.get_provider()
                
                # force_new should create new instance
                provider2 = ProviderFactory.get_provider(force_new=True)
                
                # Verify adapter was instantiated twice
                assert mock_gemini.call_count == 2
                
                # Verify different instances returned
                assert provider1 is not provider2
    
    def test_factory_reset_clears_cache(self):
        """Test that reset_provider clears the cached instance."""
        mock_settings = Mock()
        mock_settings.llm_provider = "gemini"
        mock_settings.gemini_api_key = "test_key"
        
        with patch('app.providers.factory.get_settings', return_value=mock_settings):
            with patch('app.providers.factory.GeminiAdapter') as mock_gemini:
                mock_gemini.side_effect = [
                    Mock(spec=GeminiAdapter, model_name="gemini-2.0-flash-exp"),
                    Mock(spec=GeminiAdapter, model_name="gemini-2.0-flash-exp")
                ]
                
                # First call creates instance
                provider1 = ProviderFactory.get_provider()
                
                # Reset cache
                ProviderFactory.reset_provider()
                
                # Next call should create new instance
                provider2 = ProviderFactory.get_provider()
                
                # Verify adapter was instantiated twice
                assert mock_gemini.call_count == 2
    
    def test_factory_handles_case_insensitive_provider_names(self):
        """Test that provider names are case-insensitive."""
        mock_settings = Mock()
        mock_settings.llm_provider = "GROQ"  # Uppercase
        mock_settings.groq_api_key = "test_key"
        
        with patch('app.providers.factory.get_settings', return_value=mock_settings):
            with patch('app.providers.factory.GroqAdapter') as mock_groq:
                mock_instance = Mock(spec=GroqAdapter)
                mock_instance.model = "llama-3.3-70b-versatile"
                mock_groq.return_value = mock_instance
                
                provider = ProviderFactory.get_provider()
                
                # Verify Groq was instantiated despite uppercase
                mock_groq.assert_called_once()
    
    def test_factory_strips_whitespace_from_provider_name(self):
        """Test that whitespace is stripped from provider names."""
        mock_settings = Mock()
        mock_settings.llm_provider = "  gemini  "  # With whitespace
        mock_settings.gemini_api_key = "test_key"
        
        with patch('app.providers.factory.get_settings', return_value=mock_settings):
            with patch('app.providers.factory.GeminiAdapter') as mock_gemini:
                mock_gemini.return_value = Mock(spec=GeminiAdapter, model_name="gemini-2.0-flash-exp")
                
                provider = ProviderFactory.get_provider()
                
                # Verify Gemini was instantiated despite whitespace
                mock_gemini.assert_called_once()
    
    def test_get_llm_provider_convenience_function(self):
        """Test that get_llm_provider convenience function works."""
        mock_settings = Mock()
        mock_settings.llm_provider = "gemini"
        mock_settings.gemini_api_key = "test_key"
        
        with patch('app.providers.factory.get_settings', return_value=mock_settings):
            with patch('app.providers.factory.GeminiAdapter') as mock_gemini:
                mock_gemini.return_value = Mock(spec=GeminiAdapter, model_name="gemini-2.0-flash-exp")
                
                provider = get_llm_provider()
                
                # Verify provider was created
                mock_gemini.assert_called_once()
