"""Tests for the LLM test router."""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.providers.base import LLMResponse, ProviderError, RateLimitError, InvalidKeyError, TimeoutError


client = TestClient(app)


class TestLLMTestRouter:
    """Tests for LLM test router endpoints."""
    
    def test_get_provider_info_success(self):
        """Test getting provider info when provider is configured."""
        mock_provider = Mock()
        mock_provider.name = "gemini"
        mock_provider.model_name = "gemini-2.0-flash-exp"
        # Ensure model attribute also exists and is a string
        type(mock_provider).model = property(lambda self: "gemini-2.0-flash-exp")
        
        with patch('app.routers.llm_test.get_llm_provider', return_value=mock_provider):
            response = client.get("/api/v1/llm-test/provider-info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider_name"] == "gemini"
        assert data["status"] == "active"
        assert data["model"] == "gemini-2.0-flash-exp"
    
    def test_get_provider_info_with_model_attribute(self):
        """Test getting provider info when provider uses 'model' instead of 'model_name'."""
        mock_provider = Mock()
        mock_provider.name = "groq"
        mock_provider.model = "llama-3.3-70b-versatile"
        # Remove model_name attribute
        delattr(mock_provider, 'model_name')
        
        with patch('app.routers.llm_test.get_llm_provider', return_value=mock_provider):
            response = client.get("/api/v1/llm-test/provider-info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["provider_name"] == "groq"
        assert data["model"] == "llama-3.3-70b-versatile"
    
    def test_generate_success(self):
        """Test successful text generation."""
        mock_provider = Mock()
        mock_provider.generate.return_value = LLMResponse(
            content="I'm here to help you with your health concerns.",
            provider_name="gemini",
            tokens_used=25,
            latency_ms=150.5
        )
        
        with patch('app.routers.llm_test.get_llm_provider', return_value=mock_provider):
            response = client.post(
                "/api/v1/llm-test/generate",
                json={
                    "prompt": "I'm feeling stressed",
                    "counselor_category": "Health",
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "I'm here to help you with your health concerns."
        assert data["provider_name"] == "gemini"
        assert data["tokens_used"] == 25
        assert data["latency_ms"] == 150.5
        assert data["counselor_category"] == "Health"
        
        # Verify provider was called correctly
        mock_provider.generate.assert_called_once()
        call_args = mock_provider.generate.call_args
        assert call_args.kwargs["prompt"] == "I'm feeling stressed"
        assert "health" in call_args.kwargs["system_message"].lower()
        assert call_args.kwargs["temperature"] == 0.7
        assert call_args.kwargs["max_tokens"] == 100
    
    def test_generate_with_different_categories(self):
        """Test generation with different counselor categories."""
        categories = ["Health", "Career", "Academic", "Financial", "Social", "PersonalDevelopment"]
        
        for category in categories:
            mock_provider = Mock()
            mock_provider.generate.return_value = LLMResponse(
                content=f"Response for {category}",
                provider_name="gemini",
                tokens_used=20,
                latency_ms=100.0
            )
            
            with patch('app.routers.llm_test.get_llm_provider', return_value=mock_provider):
                response = client.post(
                    "/api/v1/llm-test/generate",
                    json={
                        "prompt": "Test prompt",
                        "counselor_category": category
                    }
                )
            
            assert response.status_code == 200
            data = response.json()
            assert data["counselor_category"] == category
    
    def test_generate_handles_invalid_key_error(self):
        """Test handling of invalid API key error."""
        mock_provider = Mock()
        mock_provider.generate.side_effect = InvalidKeyError("API key invalid")
        
        with patch('app.routers.llm_test.get_llm_provider', return_value=mock_provider):
            response = client.post(
                "/api/v1/llm-test/generate",
                json={"prompt": "test", "counselor_category": "Health"}
            )
        
        assert response.status_code == 500
        assert "configuration error" in response.json()["detail"].lower()
    
    def test_generate_handles_rate_limit_error(self):
        """Test handling of rate limit error."""
        mock_provider = Mock()
        mock_provider.generate.side_effect = RateLimitError("Rate limit exceeded")
        
        with patch('app.routers.llm_test.get_llm_provider', return_value=mock_provider):
            response = client.post(
                "/api/v1/llm-test/generate",
                json={"prompt": "test", "counselor_category": "Health"}
            )
        
        assert response.status_code == 429
        assert "rate limit" in response.json()["detail"].lower()
    
    def test_generate_handles_timeout_error(self):
        """Test handling of timeout error."""
        mock_provider = Mock()
        mock_provider.generate.side_effect = TimeoutError("Request timed out")
        
        with patch('app.routers.llm_test.get_llm_provider', return_value=mock_provider):
            response = client.post(
                "/api/v1/llm-test/generate",
                json={"prompt": "test", "counselor_category": "Health"}
            )
        
        assert response.status_code == 504
        assert "timed out" in response.json()["detail"].lower()
    
    def test_generate_handles_provider_error(self):
        """Test handling of general provider error."""
        mock_provider = Mock()
        mock_provider.generate.side_effect = ProviderError("Provider error")
        
        with patch('app.routers.llm_test.get_llm_provider', return_value=mock_provider):
            response = client.post(
                "/api/v1/llm-test/generate",
                json={"prompt": "test", "counselor_category": "Health"}
            )
        
        assert response.status_code == 500
        assert "provider error" in response.json()["detail"].lower()
    
    def test_generate_with_default_parameters(self):
        """Test generation with default temperature and max_tokens."""
        mock_provider = Mock()
        mock_provider.generate.return_value = LLMResponse(
            content="Response",
            provider_name="gemini",
            tokens_used=10,
            latency_ms=50.0
        )
        
        with patch('app.routers.llm_test.get_llm_provider', return_value=mock_provider):
            response = client.post(
                "/api/v1/llm-test/generate",
                json={"prompt": "test"}  # Only required field
            )
        
        assert response.status_code == 200
        
        # Verify defaults were used
        call_args = mock_provider.generate.call_args
        assert call_args.kwargs["temperature"] == 0.7
        assert call_args.kwargs["max_tokens"] == 200  # Changed from default 500 in base
