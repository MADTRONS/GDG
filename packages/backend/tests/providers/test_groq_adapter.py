"""Tests for Groq LLM provider adapter."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from groq import APIError, RateLimitError as GroqRateLimitError, APITimeoutError, AuthenticationError

from app.providers.groq_adapter import GroqAdapter
from app.providers.base import LLMResponse, ProviderError, RateLimitError, InvalidKeyError, TimeoutError


class TestGroqAdapter:
    """Tests for GroqAdapter."""
    
    def test_groq_adapter_initialization(self):
        """Test that GroqAdapter can be initialized with an API key."""
        with patch('app.providers.groq_adapter.Groq'):
            adapter = GroqAdapter(api_key="test_groq_key")
            assert adapter.api_key == "test_groq_key"
            assert adapter.name == "groq"
            assert adapter.model == GroqAdapter.DEFAULT_MODEL
    
    def test_groq_adapter_custom_model(self):
        """Test GroqAdapter with custom model."""
        with patch('app.providers.groq_adapter.Groq'):
            adapter = GroqAdapter(api_key="test_key", model="llama-3.1-8b-instant")
            assert adapter.model == "llama-3.1-8b-instant"
    
    def test_groq_adapter_rejects_empty_key(self):
        """Test that GroqAdapter rejects empty API key."""
        with pytest.raises(InvalidKeyError):
            GroqAdapter(api_key="")
    
    def test_groq_generate_success(self):
        """Test successful response generation from Groq."""
        # Mock the Groq client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="This is a test response from Groq"))]
        mock_response.usage = Mock(total_tokens=45)
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('app.providers.groq_adapter.Groq', return_value=mock_client):
            adapter = GroqAdapter(api_key="test_key")
            
            response = adapter.generate(
                prompt="Hello, how are you?",
                system_message="You are a helpful assistant",
                temperature=0.7,
                max_tokens=100
            )
        
        # Verify the response
        assert isinstance(response, LLMResponse)
        assert response.content == "This is a test response from Groq"
        assert response.provider_name == "groq"
        assert response.tokens_used == 45
        assert response.latency_ms > 0
        
        # Verify API was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        assert call_args.kwargs['model'] == GroqAdapter.DEFAULT_MODEL
        assert call_args.kwargs['temperature'] == 0.7
        assert call_args.kwargs['max_tokens'] == 100
        assert len(call_args.kwargs['messages']) == 2
        assert call_args.kwargs['messages'][0]['role'] == 'system'
        assert call_args.kwargs['messages'][1]['role'] == 'user'
    
    def test_groq_generate_handles_authentication_error(self):
        """Test that authentication errors are properly converted."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = AuthenticationError(
            "Invalid API key", response=Mock(status_code=401), body={}
        )
        
        with patch('app.providers.groq_adapter.Groq', return_value=mock_client):
            adapter = GroqAdapter(api_key="invalid_key")
            
            with pytest.raises(InvalidKeyError) as exc_info:
                adapter.generate("test", "test")
            
            assert "authentication failed" in str(exc_info.value).lower()
    
    def test_groq_generate_handles_rate_limit_error(self):
        """Test that rate limit errors are properly converted."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = GroqRateLimitError(
            "Rate limit exceeded", response=Mock(status_code=429), body={}
        )
        
        with patch('app.providers.groq_adapter.Groq', return_value=mock_client):
            adapter = GroqAdapter(api_key="test_key")
            
            with pytest.raises(RateLimitError) as exc_info:
                adapter.generate("test", "test")
            
            assert "rate limit" in str(exc_info.value).lower()
    
    def test_groq_generate_handles_timeout_error(self):
        """Test that timeout errors are properly converted."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = APITimeoutError("Request timeout")
        
        with patch('app.providers.groq_adapter.Groq', return_value=mock_client):
            adapter = GroqAdapter(api_key="test_key")
            
            with pytest.raises(TimeoutError) as exc_info:
                adapter.generate("test", "test")
            
            assert "timed out" in str(exc_info.value).lower()
    
    def test_groq_generate_handles_api_error(self):
        """Test that general API errors are properly converted."""
        mock_client = Mock()
        
        # Create a custom exception class that looks like APIError
        class MockAPIError(Exception):
            pass
        
        mock_client.chat.completions.create.side_effect = MockAPIError("API error")
        
        with patch('app.providers.groq_adapter.Groq', return_value=mock_client):
            with patch('app.providers.groq_adapter.APIError', MockAPIError):
                adapter = GroqAdapter(api_key="test_key")
                
                with pytest.raises(ProviderError) as exc_info:
                    adapter.generate("test", "test")
                
                assert "API error" in str(exc_info.value)
    
    def test_groq_generate_handles_unexpected_error(self):
        """Test that unexpected errors are properly wrapped."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = ValueError("Unexpected error")
        
        with patch('app.providers.groq_adapter.Groq', return_value=mock_client):
            adapter = GroqAdapter(api_key="test_key")
            
            with pytest.raises(ProviderError) as exc_info:
                adapter.generate("test", "test")
            
            assert "Unexpected error" in str(exc_info.value)
    
    def test_groq_generate_with_empty_response(self):
        """Test handling of empty response content."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=None))]
        mock_response.usage = Mock(total_tokens=10)
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('app.providers.groq_adapter.Groq', return_value=mock_client):
            adapter = GroqAdapter(api_key="test_key")
            
            response = adapter.generate("test", "test")
            
            assert response.content == ""
            assert response.tokens_used == 10
    
    def test_groq_generate_with_missing_usage(self):
        """Test handling of response without usage information."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_response.usage = None
        mock_client.chat.completions.create.return_value = mock_response
        
        with patch('app.providers.groq_adapter.Groq', return_value=mock_client):
            adapter = GroqAdapter(api_key="test_key")
            
            response = adapter.generate("test", "test")
            
            assert response.content == "Test response"
            assert response.tokens_used == 0
