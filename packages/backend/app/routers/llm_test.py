"""
Test router for LLM provider abstraction.

This router demonstrates the universal LLM provider usage across all counselor categories.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict

from app.providers import get_llm_provider, ProviderError, RateLimitError, InvalidKeyError, TimeoutError


router = APIRouter(
    prefix="/llm-test",
    tags=["LLM Test"]
)


class TestPromptRequest(BaseModel):
    """Request model for testing LLM provider."""
    prompt: str
    counselor_category: str = "Health"
    temperature: float = 0.7
    max_tokens: int = 200


class TestPromptResponse(BaseModel):
    """Response model for LLM test."""
    content: str
    provider_name: str
    tokens_used: int
    latency_ms: float
    counselor_category: str


# Category system prompts for demonstration
CATEGORY_PROMPTS = {
    "Health": "You are a compassionate health and wellness counselor for college students.",
    "Career": "You are an experienced career counselor helping college students plan their future.",
    "Academic": "You are a supportive academic counselor helping students succeed in their studies.",
    "Financial": "You are a knowledgeable financial aid counselor helping students manage finances.",
    "Social": "You are an empathetic social counselor helping students with relationships and social issues.",
    "PersonalDevelopment": "You are a personal development counselor helping students grow and discover themselves.",
}


@router.post(
    "/generate",
    response_model=TestPromptResponse,
    summary="Test LLM provider with counselor category",
    description="Generate a response using the configured LLM provider (Groq or Gemini) for any counselor category."
)
async def test_generate(request: TestPromptRequest) -> TestPromptResponse:
    """
    Test the universal LLM provider with a prompt and counselor category.
    
    This endpoint demonstrates that the same provider instance is used across
    all counselor categories, regardless of which one is selected.
    """
    try:
        # Get the universal provider (same instance for all categories)
        provider = get_llm_provider()
        
        # Get category-specific system prompt
        system_message = CATEGORY_PROMPTS.get(
            request.counselor_category,
            "You are a helpful counselor for college students."
        )
        
        # Generate response using the provider
        response = provider.generate(
            prompt=request.prompt,
            system_message=system_message,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return TestPromptResponse(
            content=response.content,
            provider_name=response.provider_name,
            tokens_used=response.tokens_used,
            latency_ms=response.latency_ms,
            counselor_category=request.counselor_category
        )
    
    except InvalidKeyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM provider configuration error: {str(e)}"
        )
    
    except RateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"LLM provider rate limit exceeded: {str(e)}"
        )
    
    except TimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"LLM provider request timed out: {str(e)}"
        )
    
    except ProviderError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM provider error: {str(e)}"
        )


@router.get(
    "/provider-info",
    summary="Get current LLM provider information",
    description="Returns information about the currently configured LLM provider."
)
async def get_provider_info() -> Dict[str, str]:
    """
    Get information about the configured LLM provider.
    
    Returns the provider name and model being used.
    """
    try:
        provider = get_llm_provider()
        
        # Get provider-specific info
        info = {
            "provider_name": provider.name,
            "status": "active"
        }
        
        # Add model info if available
        if hasattr(provider, 'model'):
            info["model"] = provider.model
        elif hasattr(provider, 'model_name'):
            info["model"] = provider.model_name
        
        return info
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get provider info: {str(e)}"
        )
