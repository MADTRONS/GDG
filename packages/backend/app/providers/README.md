# LLM Provider Abstraction

Universal LLM provider abstraction layer for the College Student Counseling Platform.

## Overview

This module provides a unified interface for interacting with multiple LLM providers (Groq, Gemini) across all counselor categories in the system. The abstraction allows easy switching between providers via environment configuration without code changes.

## Architecture

- **Base Layer**: `LLMProvider` abstract base class defines the interface
- **Adapters**: Provider-specific implementations (GroqAdapter, GeminiAdapter)
- **Factory**: Singleton pattern for provider instantiation
- **Response Format**: Standardized `LLMResponse` dataclass

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Choose provider: "groq" or "gemini" (default: gemini)
LLM_PROVIDER=gemini

# Provider API Keys (configure both, only active one is used)
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### Supported Providers

#### Groq
- **Model**: llama-3.3-70b-versatile (default)
- **Features**: Fast inference, OpenAI-compatible API
- **Pricing**: Competitive per-token pricing

#### Gemini
- **Model**: gemini-2.0-flash-exp (default)
- **Features**: Strong reasoning, safety filters
- **Pricing**: Generous free tier, pay-as-you-go

## Usage

### Basic Usage

```python
from app.providers import get_llm_provider

# Get the configured provider (singleton instance)
provider = get_llm_provider()

# Generate response
response = provider.generate(
    prompt="I'm feeling stressed about exams",
    system_message="You are a compassionate health counselor for college students.",
    temperature=0.7,
    max_tokens=500
)

print(f"Provider: {response.provider_name}")
print(f"Response: {response.content}")
print(f"Tokens used: {response.tokens_used}")
print(f"Latency: {response.latency_ms}ms")
```

### Using with Counselor Categories

```python
from app.providers import get_llm_provider

CATEGORY_PROMPTS = {
    "Health": "You are a compassionate health and wellness counselor...",
    "Career": "You are an experienced career counselor...",
    "Academic": "You are a supportive academic counselor...",
    # ... other categories
}

def generate_counselor_response(prompt: str, category: str):
    provider = get_llm_provider()
    system_message = CATEGORY_PROMPTS.get(category)
    
    response = provider.generate(
        prompt=prompt,
        system_message=system_message,
        temperature=0.7,
        max_tokens=500
    )
    
    return response.content
```

### Error Handling

```python
from app.providers import (
    get_llm_provider,
    ProviderError,
    RateLimitError,
    InvalidKeyError,
    TimeoutError
)

try:
    provider = get_llm_provider()
    response = provider.generate(
        prompt="Hello",
        system_message="You are a helpful counselor"
    )
except InvalidKeyError as e:
    print(f"API key error: {e}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except TimeoutError as e:
    print(f"Request timeout: {e}")
except ProviderError as e:
    print(f"Provider error: {e}")
```

## Testing

### Test the Provider

Use the test endpoint to verify provider configuration:

```bash
# Get provider info
curl http://localhost:8000/api/v1/llm-test/provider-info

# Test generation
curl -X POST http://localhost:8000/api/v1/llm-test/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "I need help with career planning",
    "counselor_category": "Career",
    "temperature": 0.7,
    "max_tokens": 200
  }'
```

### Run Unit Tests

```bash
# Test all provider components
pytest tests/providers/ -v

# Test specific adapter
pytest tests/providers/test_groq_adapter.py -v
pytest tests/providers/test_gemini_adapter.py -v

# Test factory
pytest tests/providers/test_factory.py -v
```

## Switching Providers

To switch from Gemini to Groq:

1. Update `.env`:
   ```bash
   LLM_PROVIDER=groq
   ```

2. Restart the application:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Verify the change:
   ```bash
   curl http://localhost:8000/api/v1/llm-test/provider-info
   ```

## Adding a New Provider

To add support for a new provider (e.g., Claude):

1. Create adapter: `app/providers/claude_adapter.py`
2. Implement `LLMProvider` interface
3. Add to factory: `app/providers/factory.py`
4. Update config: `app/config.py`
5. Add tests: `tests/providers/test_claude_adapter.py`

Example adapter structure:

```python
from .base import LLMProvider, LLMResponse

class ClaudeAdapter(LLMProvider):
    DEFAULT_MODEL = "claude-3-sonnet"
    
    def __init__(self, api_key: str, model: str = None):
        super().__init__(api_key)
        self.model = model or self.DEFAULT_MODEL
        # Initialize Claude client
    
    @property
    def name(self) -> str:
        return "claude"
    
    def generate(self, prompt, system_message, temperature=0.7, max_tokens=500):
        # Implement Claude API call
        # Return LLMResponse
        pass
```

## Performance

- **Latency Overhead**: <50ms abstraction layer overhead
- **Concurrent Requests**: Supports 10+ simultaneous sessions
- **Token Tracking**: Automatic token usage reporting
- **Caching**: Singleton provider instance for efficiency

## Troubleshooting

### Provider not initializing

**Error**: `ValueError: GEMINI_API_KEY is required`

**Solution**: Ensure API key is set in `.env` file for the selected provider.

### Rate limit errors

**Error**: `RateLimitError: Rate limit exceeded`

**Solution**: 
- Wait and retry with exponential backoff
- Upgrade to paid tier for higher limits
- Switch to alternative provider

### Invalid responses

**Error**: `ProviderError: Response blocked by safety filters`

**Solution** (Gemini-specific):
- Adjust system prompt to avoid triggering filters
- Review prompt content for sensitive topics

## API Reference

### LLMProvider (Abstract Base Class)

```python
class LLMProvider(ABC):
    def __init__(self, api_key: str): ...
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_message: str,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> LLMResponse: ...
    
    @property
    @abstractmethod
    def name(self) -> str: ...
```

### LLMResponse (Data Class)

```python
@dataclass
class LLMResponse:
    content: str           # Generated text
    provider_name: str     # Provider identifier
    tokens_used: int       # Total tokens consumed
    latency_ms: float      # Response latency
```

### ProviderFactory

```python
class ProviderFactory:
    @staticmethod
    def get_provider(force_new: bool = False) -> LLMProvider:
        """Get configured provider instance (singleton)"""
        
    @staticmethod
    def reset_provider() -> None:
        """Clear cached provider instance"""
```

## License

Internal use only - College Student Counseling Platform.
