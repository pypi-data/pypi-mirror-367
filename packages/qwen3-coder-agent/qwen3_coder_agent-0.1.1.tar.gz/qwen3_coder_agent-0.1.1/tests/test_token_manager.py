"""Tests for token_manager.py"""
import pytest
from unittest.mock import Mock, patch
from qwen3_coder.token_manager import TokenManager
from qwen3_coder.exceptions import TokenLimitExceededError
from qwen3_coder.config import config

@pytest.fixture
def token_manager():
    """Fixture providing a clean TokenManager instance for each test."""
    return TokenManager()

def test_initialization(token_manager):
    """Test that TokenManager initializes with zero token counts."""
    assert token_manager.total_tokens_used == 0
    assert token_manager.prompt_tokens == 0
    assert token_manager.completion_tokens == 0
    assert token_manager.validation_samples == []

def test_count_tokens_basic(token_manager):
    """Test basic token counting functionality."""
    # Test with empty string
    assert token_manager.count_tokens("") == 0
    
    # Test with simple text - use more distinct test cases
    short_text = "hello"
    long_text = "This is a longer sentence that should have more tokens than a single word."
    
    count1 = token_manager.count_tokens(short_text)
    count2 = token_manager.count_tokens(long_text)
    
    assert count1 > 0, "Single word should have at least 1 token"
    assert count2 > count1, "Longer text should have more tokens than a single word"

def test_count_message_tokens(token_manager):
    """Test token counting for message lists."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
    
    token_count = token_manager.count_message_tokens(messages)
    assert token_count > 0
    
    # Adding more messages should increase token count
    more_messages = messages + [{"role": "assistant", "content": "Hi there!"}]
    assert token_manager.count_message_tokens(more_messages) > token_count

def test_check_context_limit_within_bounds(token_manager):
    """Test context limit check when within bounds."""
    messages = [{"role": "user", "content": "Short message"}]
    max_tokens = 100
    
    within_limit, total_tokens, available = token_manager.check_context_limit(messages, max_tokens)
    
    assert within_limit is True
    assert total_tokens > 0
    assert available > 0

def test_check_context_limit_exceeded(token_manager):
    """Test context limit check when exceeded."""
    # Create a very long message that will exceed the context window
    long_message = "x" * 10000
    messages = [{"role": "user", "content": long_message}]
    max_tokens = 32000  # This should exceed the default limit
    
    within_limit, total_tokens, available = token_manager.check_context_limit(messages, max_tokens)
    
    assert within_limit is False
    assert total_tokens > 0
    assert available < 0

def test_enforce_token_limit_within_bounds(token_manager):
    """Test token limit enforcement when within bounds."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
    
    # Should return the same messages since we're within limits
    result = token_manager.enforce_token_limit(messages, 100)
    assert result == messages

def test_enforce_token_limit_trimming(token_manager):
    """Test that token limit enforcement trims messages when needed."""
    # Create a list of messages that will exceed the context window
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Message 1" * 500},  # Make this large
        {"role": "assistant", "content": "Response 1" * 500},  # Make this large
        {"role": "user", "content": "Message 2" * 1000}  # This will be too large
    ]
    
    # This should trim messages to fit within limits
    result = token_manager.enforce_token_limit(messages, 100)
    
    # Should keep system message and at least one other message
    assert len(result) <= len(messages)
    assert result[0]["role"] == "system"  # System message should be kept
    
    # Verify that the total tokens are within limits
    within_limit, total_tokens, _ = token_manager.check_context_limit(result, 100)
    assert within_limit is True, f"Result should be within token limits, but got {total_tokens} tokens"

def test_enforce_token_limit_too_large_message(token_manager):
    """Test that a single message that's too large raises an appropriate error."""
    # Create a single message that's too large
    # Use a message that's larger than the maximum allowed tokens
    max_allowed = config.MAX_CONTEXT_TOKENS - 100  # 100 tokens for completion
    huge_message = "x" * (max_allowed * 10)  # Make it 10x larger than allowed
    messages = [{"role": "user", "content": huge_message}]
    
    # This should raise an error about the message being too large
    with pytest.raises(TokenLimitExceededError) as exc_info:
        token_manager.enforce_token_limit(messages, 100)
    
    assert "too large" in str(exc_info.value).lower()
    assert "tokens" in str(exc_info.value)

def test_update_usage(token_manager):
    """Test updating token usage statistics."""
    # Initial update
    token_manager.update_usage({
        'prompt_tokens': 10,
        'completion_tokens': 20,
        'total_tokens': 30
    })
    
    assert token_manager.prompt_tokens == 10
    assert token_manager.completion_tokens == 20
    assert token_manager.total_tokens_used == 30
    
    # Second update should add to the totals
    token_manager.update_usage({
        'prompt_tokens': 5,
        'completion_tokens': 15,
        'total_tokens': 20
    })
    
    assert token_manager.prompt_tokens == 15
    assert token_manager.completion_tokens == 35
    assert token_manager.total_tokens_used == 50

def test_update_usage_with_validation(token_manager):
    """Test updating usage with validation data."""
    # Mock the validation method to check if it's called
    with patch.object(token_manager, '_validate_token_counts') as mock_validate:
        token_manager.update_usage(
            {'prompt_tokens': 10, 'completion_tokens': 20, 'total_tokens': 30},
            prompt_text="test prompt",
            completion_text="test completion"
        )
        
        # Check that validation was called with the right arguments
        mock_validate.assert_called_once_with(
            "test prompt",
            "test completion",
            10,  # prompt_tokens
            20   # completion_tokens
        )

def test_validate_token_counts(token_manager):
    """Test token count validation."""
    # Initial validation should add to samples but not update ratios yet
    token_manager._validate_token_counts(
        prompt_text="test prompt",
        completion_text="test completion",
        actual_prompt_tokens=10,
        actual_completion_tokens=20
    )
    
    assert len(token_manager.validation_samples) == 1
    sample = token_manager.validation_samples[0]
    assert sample['prompt'] == "test prompt"
    assert sample['completion'] == "test completion"
    assert sample['prompt_tokens'] == 10
    assert sample['completion_tokens'] == 20

def test_update_tokenizer_ratios(token_manager):
    """Test updating tokenizer ratios from validation samples."""
    # Add some validation samples
    token_manager.validation_samples = [
        {
            'prompt': "test prompt",
            'completion': "test completion",
            'prompt_tokens': 10,
            'completion_tokens': 20,
            'timestamp': 1234567890
        }
    ]
    
    # Mock the tokenizer's validate_accuracy method
    with patch('qwen3_coder.token_utils.tokenizer.validate_accuracy') as mock_validate:
        token_manager._update_tokenizer_ratios()
        
        # Check that validate_accuracy was called with our samples
        assert mock_validate.call_count == 2  # Once for prompt, once for completion
        
        # Samples should be cleared after updating
        assert token_manager.validation_samples == []

def test_get_usage_stats(token_manager):
    """Test getting usage statistics."""
    # Set some token counts
    token_manager.prompt_tokens = 100
    token_manager.completion_tokens = 200
    token_manager.total_tokens_used = 300
    
    stats = token_manager.get_usage_stats()
    
    assert stats == {
        'prompt_tokens': 100,
        'completion_tokens': 200,
        'total_tokens': 300
    }
