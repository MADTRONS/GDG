"""Tests for the base LLM provider abstraction."""

import pytest

from app.providers.base import (
    LLMProvider,
    LLMResponse,
    ProviderError,
    RateLimitError,
    InvalidKeyError,
    TimeoutError,
)


class MockProvider(LLMProvider):
    """Mock provider for testing the abstract base class."""
    
    @property
    def name(self) -> str:
        return "mock"
    
    def generate(
        self,
        prompt: str,
        system_message: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> LLMResponse:
        """Mock implementation that returns a test response."""
        return LLMResponse(
            content=f"Mock response to: {prompt}",
            provider_name=self.name,
            tokens_used=50,
            latency_ms=100.0
        )


class TestLLMResponse:
    """Tests for the LLMResponse dataclass."""
    
    def test_llm_response_creation(self):
        """Test creating an LLMResponse with all fields."""
        response = LLMResponse(
            content="Hello, world!",
            provider_name="test_provider",
            tokens_used=10,
            latency_ms=150.5
        )
        
        assert response.content == "Hello, world!"
        assert response.provider_name == "test_provider"
        assert response.tokens_used == 10
        assert response.latency_ms == 150.5
    
    def test_llm_response_equality(self):
        """Test that two identical LLMResponse objects are equal."""
        response1 = LLMResponse("test", "provider", 10, 100.0)
        response2 = LLMResponse("test", "provider", 10, 100.0)
        
        assert response1 == response2


class TestProviderExceptions:
    """Tests for provider exception classes."""
    
    def test_provider_error(self):
        """Test ProviderError can be raised and caught."""
        with pytest.raises(ProviderError) as exc_info:
            raise ProviderError("Test error")
        
        assert str(exc_info.value) == "Test error"
    
    def test_rate_limit_error(self):
        """Test RateLimitError is a subclass of ProviderError."""
        with pytest.raises(ProviderError):
            raise RateLimitError("Rate limit exceeded")
        
        with pytest.raises(RateLimitError) as exc_info:
            raise RateLimitError("Rate limit exceeded")
        
        assert str(exc_info.value) == "Rate limit exceeded"
    
    def test_invalid_key_error(self):
        """Test InvalidKeyError is a subclass of ProviderError."""
        with pytest.raises(ProviderError):
            raise InvalidKeyError("Invalid API key")
        
        with pytest.raises(InvalidKeyError) as exc_info:
            raise InvalidKeyError("Invalid API key")
        
        assert str(exc_info.value) == "Invalid API key"
    
    def test_timeout_error(self):
        """Test TimeoutError is a subclass of ProviderError."""
        with pytest.raises(ProviderError):
            raise TimeoutError("Request timeout")
        
        with pytest.raises(TimeoutError) as exc_info:
            raise TimeoutError("Request timeout")
        
        assert str(exc_info.value) == "Request timeout"


class TestLLMProvider:
    """Tests for the LLMProvider abstract base class."""
    
    def test_provider_requires_api_key(self):
        """Test that provider initialization requires an API key."""
        provider = MockProvider(api_key="test_key_123")
        assert provider.api_key == "test_key_123"
    
    def test_provider_rejects_empty_api_key(self):
        """Test that provider raises InvalidKeyError for empty API key."""
        with pytest.raises(InvalidKeyError) as exc_info:
            MockProvider(api_key="")
        
        assert "API key is required" in str(exc_info.value)
    
    def test_provider_rejects_none_api_key(self):
        """Test that provider raises InvalidKeyError for None API key."""
        with pytest.raises(InvalidKeyError):
            MockProvider(api_key=None)  # type: ignore
    
    def test_provider_name_property(self):
        """Test that provider name property works."""
        provider = MockProvider(api_key="test_key")
        assert provider.name == "mock"
    
    def test_provider_generate_method(self):
        """Test that the generate method works on mock provider."""
        provider = MockProvider(api_key="test_key")
        
        response = provider.generate(
            prompt="Hello",
            system_message="You are a helpful assistant",
            temperature=0.7,
            max_tokens=100
        )
        
        assert isinstance(response, LLMResponse)
        assert "Hello" in response.content
        assert response.provider_name == "mock"
        assert response.tokens_used > 0
        assert response.latency_ms > 0
    
    def test_provider_generate_with_defaults(self):
        """Test generate method with default parameters."""
        provider = MockProvider(api_key="test_key")
        
        response = provider.generate(
            prompt="Test prompt",
            system_message="Test system message"
        )
        
        assert isinstance(response, LLMResponse)
        assert response.content
