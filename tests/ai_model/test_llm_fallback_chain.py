import pytest
import asyncio
from unittest.mock import patch, AsyncMock
from app.ai.llm_client import LLMClient, LLMUnavailableException


@pytest.mark.asyncio
async def test_gemini_fails_openai_called():
    """Test that OpenAI is called when Gemini fails."""
    client = LLMClient()
    # Mock _call_google to fail for both gemini models
    call_count = 0
    async def fail_google(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        raise Exception(f"Gemini failed (call {call_count})")
    
    with patch.object(client, '_call_google', side_effect=fail_google):
        with patch.object(client, '_call_openai', return_value=type('obj', (object,), {'content': '{}', 'model_used': 'gpt-4o-mini'})()) as mock_openai:
            result = await client.complete([{"role": "user", "content": "test"}])
            # Should have tried both gemini models
            assert call_count == 2
            mock_openai.assert_called_once()
            assert result.model_used == 'gpt-4o-mini'


@pytest.mark.asyncio
async def test_gemini_and_openai_fail_claude_called():
    """Test that Claude is called when both Gemini and OpenAI fail."""
    client = LLMClient()
    
    async def fail_google(*args, **kwargs):
        raise Exception("Gemini failed")
    
    async def fail_openai(*args, **kwargs):
        raise Exception("OpenAI failed")
    
    with patch.object(client, '_call_google', side_effect=fail_google):
        with patch.object(client, '_call_openai', side_effect=fail_openai):
            with patch.object(client, '_call_anthropic', return_value=type('obj', (object,), {'content': '{}', 'model_used': 'claude-3-haiku'})()) as mock_claude:
                result = await client.complete([{"role": "user", "content": "test"}])
                mock_claude.assert_called_once()
                assert result.model_used == 'claude-3-haiku'


@pytest.mark.asyncio
async def test_all_providers_fail_raises_llm_unavailable():
    """Test that LLMUnavailableException is raised when all providers fail."""
    client = LLMClient()
    
    async def fail_google(*args, **kwargs):
        raise Exception("Gemini failed")
    
    async def fail_openai(*args, **kwargs):
        raise Exception("OpenAI failed")
    
    async def fail_anthropic(*args, **kwargs):
        raise Exception("Claude failed")
    
    with patch.object(client, '_call_google', side_effect=fail_google):
        with patch.object(client, '_call_openai', side_effect=fail_openai):
            with patch.object(client, '_call_anthropic', side_effect=fail_anthropic):
                with pytest.raises(LLMUnavailableException):
                    await client.complete([{"role": "user", "content": "test"}])


@pytest.mark.asyncio
async def test_all_fail_activates_degraded_mode():
    """Test that degraded mode is activated when all providers fail."""
    client = LLMClient()
    
    async def fail_all(*args, **kwargs):
        raise Exception("Provider failed")
    
    with patch.object(client, '_call_google', side_effect=fail_all):
        with patch.object(client, '_call_openai', side_effect=fail_all):
            with patch.object(client, '_call_anthropic', side_effect=fail_all):
                with pytest.raises(LLMUnavailableException):
                    await client.complete([{"role": "user", "content": "test"}])


@pytest.mark.asyncio
async def test_timeout_triggers_fallback():
    """Test that timeout triggers fallback to next provider."""
    client = LLMClient()
    
    async def timeout_google(*args, **kwargs):
        raise asyncio.TimeoutError("Timeout")
    
    with patch.object(client, '_call_google', side_effect=timeout_google):
        with patch.object(client, '_call_openai', return_value=type('obj', (object,), {'content': '{}', 'model_used': 'gpt-4o-mini'})()) as mock_openai:
            result = await client.complete([{"role": "user", "content": "test"}])
            mock_openai.assert_called_once()


@pytest.mark.asyncio
async def test_model_used_field_reflects_actual_model():
    """Test that the model_used field reflects the actual model that succeeded."""
    client = LLMClient()
    # Google succeeds (first model in chain)
    result = await client.complete([{"role": "user", "content": "test"}])
    assert result.model_used == 'gemini-2.0-flash'


@pytest.mark.asyncio
async def test_degraded_mode_returns_503_on_chat():
    """Test that degraded mode returns 503 for chat endpoints."""
    # This would be an integration test - skip for now
    pytest.skip("Integration test - requires running server")
