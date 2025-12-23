"""Tests for Gemini LLM provider adapter."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from google.api_core import exceptions as google_exceptions

from app.providers.gemini_adapter import GeminiAdapter
from app.providers.base import LLMResponse, ProviderError, RateLimitError, InvalidKeyError, TimeoutError


class TestGeminiAdapter:
    """Tests for GeminiAdapter."""
    
    def test_gemini_adapter_initialization(self):
        """Test that GeminiAdapter can be initialized with an API key."""
        with patch('app.providers.gemini_adapter.genai'):
            adapter = GeminiAdapter(api_key="test_gemini_key")
            assert adapter.api_key == "test_gemini_key"
            assert adapter.name == "gemini"
            assert adapter.model_name == GeminiAdapter.DEFAULT_MODEL
    
    def test_gemini_adapter_custom_model(self):
        """Test GeminiAdapter with custom model."""
        with patch('app.providers.gemini_adapter.genai'):
            adapter = GeminiAdapter(api_key="test_key", model="gemini-pro")
            assert adapter.model_name == "gemini-pro"
    
    def test_gemini_adapter_rejects_empty_key(self):
        """Test that GeminiAdapter rejects empty API key."""
        with pytest.raises(InvalidKeyError):
            GeminiAdapter(api_key="")
    
    def test_gemini_generate_success(self):
        """Test successful response generation from Gemini."""
        # Mock the genai module and model
        mock_genai = Mock()
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "This is a test response from Gemini"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch('app.providers.gemini_adapter.genai', mock_genai):
            adapter = GeminiAdapter(api_key="test_key")
            
            response = adapter.generate(
                prompt="Hello, how are you?",
                system_message="You are a helpful assistant",
                temperature=0.7,
                max_tokens=100
            )
        
        # Verify the response
        assert isinstance(response, LLMResponse)
        assert response.content == "This is a test response from Gemini"
        assert response.provider_name == "gemini"
        assert response.tokens_used > 0
        assert response.latency_ms > 0
        
        # Verify API was called correctly
        mock_model.generate_content.assert_called_once()
        call_args = mock_model.generate_content.call_args
        assert "helpful assistant" in call_args.args[0]
        assert "Hello, how are you?" in call_args.args[0]
    
    def test_gemini_generate_handles_unauthenticated_error(self):
        """Test that authentication errors are properly converted."""
        mock_genai = Mock()
        mock_model = Mock()
        mock_model.generate_content.side_effect = google_exceptions.Unauthenticated("Invalid API key")
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch('app.providers.gemini_adapter.genai', mock_genai):
            adapter = GeminiAdapter(api_key="invalid_key")
            
            with pytest.raises(InvalidKeyError) as exc_info:
                adapter.generate("test", "test")
            
            assert "authentication failed" in str(exc_info.value).lower()
    
    def test_gemini_generate_handles_rate_limit_error(self):
        """Test that rate limit errors are properly converted."""
        mock_genai = Mock()
        mock_model = Mock()
        mock_model.generate_content.side_effect = google_exceptions.ResourceExhausted("Quota exceeded")
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch('app.providers.gemini_adapter.genai', mock_genai):
            adapter = GeminiAdapter(api_key="test_key")
            
            with pytest.raises(RateLimitError) as exc_info:
                adapter.generate("test", "test")
            
            assert "rate limit" in str(exc_info.value).lower()
    
    def test_gemini_generate_handles_timeout_error(self):
        """Test that timeout errors are properly converted."""
        mock_genai = Mock()
        mock_model = Mock()
        mock_model.generate_content.side_effect = google_exceptions.DeadlineExceeded("Deadline exceeded")
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch('app.providers.gemini_adapter.genai', mock_genai):
            adapter = GeminiAdapter(api_key="test_key")
            
            with pytest.raises(TimeoutError) as exc_info:
                adapter.generate("test", "test")
            
            assert "timed out" in str(exc_info.value).lower()
    
    def test_gemini_generate_handles_google_api_error(self):
        """Test that general Google API errors are properly converted."""
        mock_genai = Mock()
        mock_model = Mock()
        mock_model.generate_content.side_effect = google_exceptions.GoogleAPIError("API error")
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch('app.providers.gemini_adapter.genai', mock_genai):
            adapter = GeminiAdapter(api_key="test_key")
            
            with pytest.raises(ProviderError) as exc_info:
                adapter.generate("test", "test")
            
            assert "API error" in str(exc_info.value)
    
    def test_gemini_generate_handles_safety_filter(self):
        """Test that safety filter blocks are properly handled."""
        mock_genai = Mock()
        mock_model = Mock()
        mock_model.generate_content.side_effect = ValueError("Response blocked by safety filter")
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch('app.providers.gemini_adapter.genai', mock_genai):
            adapter = GeminiAdapter(api_key="test_key")
            
            with pytest.raises(ProviderError) as exc_info:
                adapter.generate("test", "test")
            
            assert "safety" in str(exc_info.value).lower()
    
    def test_gemini_generate_handles_missing_text_attribute(self):
        """Test handling of response with no text attribute due to safety filters."""
        mock_genai = Mock()
        mock_model = Mock()
        mock_response = Mock(spec=[])  # Mock with no 'text' attribute
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch('app.providers.gemini_adapter.genai', mock_genai):
            adapter = GeminiAdapter(api_key="test_key")
            
            with pytest.raises(ProviderError) as exc_info:
                adapter.generate("test", "test")
            
            assert "safety filter" in str(exc_info.value).lower() or "response" in str(exc_info.value).lower()
    
    def test_gemini_generate_with_empty_response(self):
        """Test handling of empty response text."""
        mock_genai = Mock()
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = ""
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch('app.providers.gemini_adapter.genai', mock_genai):
            adapter = GeminiAdapter(api_key="test_key")
            
            response = adapter.generate("test", "test")
            
            assert response.content == ""
            assert response.tokens_used > 0  # Still estimates tokens from input
    
    def test_gemini_generate_handles_unexpected_error(self):
        """Test that unexpected errors are properly wrapped."""
        mock_genai = Mock()
        mock_model = Mock()
        mock_model.generate_content.side_effect = RuntimeError("Unexpected error")
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch('app.providers.gemini_adapter.genai', mock_genai):
            adapter = GeminiAdapter(api_key="test_key")
            
            with pytest.raises(ProviderError) as exc_info:
                adapter.generate("test", "test")
            
            assert "Unexpected error" in str(exc_info.value)
    
    def test_gemini_token_estimation(self):
        """Test token estimation logic."""
        mock_genai = Mock()
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Response"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        with patch('app.providers.gemini_adapter.genai', mock_genai):
            adapter = GeminiAdapter(api_key="test_key")
            
            response = adapter.generate(
                prompt="Short prompt",
                system_message="System message"
            )
            
            # Token count should be estimated based on character count
            assert response.tokens_used > 0
