"""Tests for token_utils.py"""
import pytest
from qwen3_coder.token_utils import QwenTokenizer

# Sample test cases with different text types
TEST_CASES = [
    # (text, expected_type, description)
    ("", "whitespace", "empty string"),
    (" ", "whitespace", "whitespace only"),
    ("\n\n", "whitespace", "newlines only"),
    ("# This is a comment", "comment", "single line comment"),
    ("def hello():\n    print('Hello, world!')", "code", "simple function"),
    ("""
    /*
    Multi-line
    comment
    */
    """, "comment", "multi-line comment"),
    ("```python\nprint('code block')\n```", "code", "code block"),
    ("This is regular text", "markdown", "regular text"),
    ("# Heading\n\nSome text with `inline code`", "markdown", "markdown with code"),
]

@pytest.fixture
def tokenizer():
    """Fixture providing a clean tokenizer instance for each test."""
    return QwenTokenizer()

def test_tokenizer_initialization(tokenizer):
    """Test that the tokenizer initializes with default ratios."""
    assert hasattr(tokenizer, 'token_ratios')
    assert 'code' in tokenizer.token_ratios
    assert 'comment' in tokenizer.token_ratios
    assert 'whitespace' in tokenizer.token_ratios
    assert 'markdown' in tokenizer.token_ratios

def test_text_classification(tokenizer):
    """Test that text is correctly classified by type."""
    for text, expected_type, description in TEST_CASES:
        result = tokenizer._classify_text(text)
        print(f"\nTest case: {description}")
        print(f"Text: {text!r}")
        print(f"Expected: {expected_type}, Got: {result}")
        assert result == expected_type, f"Failed on: {description}"

def test_token_counting_basic(tokenizer):
    """Test basic token counting functionality."""
    # Simple test cases
    assert tokenizer.count_tokens("") == 0
    assert tokenizer.count_tokens("hello") > 0
    assert tokenizer.count_tokens("hello world") > tokenizer.count_tokens("hello")

def test_token_counting_code_vs_text(tokenizer):
    """Test that code and text are tokenized differently."""
    code = "def hello():\n    return 'world'"
    text = "This is a function that returns 'world'"
    
    # Code should generally use more tokens than equivalent text
    code_tokens = tokenizer.count_tokens(code)
    text_tokens = tokenizer.count_tokens(text)
    
    # The exact ratio might vary, but code should be more verbose
    assert code_tokens > text_tokens * 0.8  # Allow some flexibility

def test_message_token_counting(tokenizer):
    """Test token counting for chat messages."""
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm doing well, thank you!"}
    ]
    
    token_count = tokenizer.count_message_tokens(messages)
    assert token_count > 0
    
    # Adding more messages should increase token count
    more_messages = messages + [{"role": "user", "content": "Tell me more"}]
    assert tokenizer.count_message_tokens(more_messages) > token_count

def test_token_ratio_updates(tokenizer):
    """Test that token ratios update based on validation data."""
    # Get initial ratio for code
    initial_ratio = tokenizer.token_ratios['code']
    
    # Simulate API feedback that code uses more tokens than we estimated
    code_sample = "def test():\n    return 42"
    actual_tokens = 15  # Let's say the API reports more tokens than we estimated
    
    # Update ratios with validation data
    tokenizer.update_ratios({
        code_sample: actual_tokens
    })
    
    # The ratio should have increased to account for the underestimation
    assert tokenizer.token_ratios['code'] > initial_ratio

def test_validation_accuracy(tokenizer):
    """Test the validation accuracy reporting."""
    # Create test samples with known token counts
    test_samples = [
        ("hello world", 2),
        ("This is a test", 4),
        ("def test():\n    pass", 6)
    ]
    
    # Validate accuracy
    metrics = tokenizer.validate_accuracy(test_samples)
    
    # Check that metrics are calculated correctly
    assert 'average_difference' in metrics
    assert 'average_percentage_difference' in metrics
    assert 'total_actual' in metrics
    assert 'total_estimate' in metrics
    assert 'samples' in metrics
    
    assert metrics['samples'] == len(test_samples)
    assert metrics['total_actual'] == sum(t[1] for t in test_samples)

def test_empty_validation(tokenizer):
    """Test validation with empty input."""
    metrics = tokenizer.validate_accuracy([])
    assert metrics['samples'] == 0
    assert metrics['total_actual'] == 0
    assert metrics['total_estimate'] == 0

def test_ratio_updates_from_estimates(tokenizer):
    """Test that ratios are updated based on accumulated estimates."""
    # Store initial ratios
    initial_ratios = tokenizer.token_ratios.copy()
    print(f"Initial ratios: {initial_ratios}")
    
    # Add some validation samples with higher actual token counts
    # We need at least 3 samples per text type to trigger ratio updates
    test_samples = [
        # Comment samples (type: comment)
        ("# comment 1", 10),  # Actual is more than estimated
        ("# comment 2", 12),  # Actual is more than estimated
        ("# comment 3", 15),  # Actual is more than estimated
        
        # Markdown samples (type: markdown)
        ("sample text 1", 8),   # Actual is more than estimated
        ("sample text 2", 10),  # Actual is more than estimated
        ("sample text 3", 12),  # Actual is more than estimated
        
        # Code samples (type: code)
        ("def func1(): pass", 20),  # Actual is more than estimated
        ("x = 1 + 2", 15),         # Actual is more than estimated
        ("for i in range(3):\n    print(i)", 25)  # Actual is more than estimated
    ]
    
    # Print debug info for each sample
    for text, actual in test_samples:
        text_type = tokenizer._classify_text(text)
        estimate = tokenizer._estimate_tokens(text)
        print(f"Sample: {text!r} (type: {text_type}) - Estimate: {estimate}, Actual: {actual}")
    
    # Run validation to accumulate estimates
    metrics = tokenizer.validate_accuracy(test_samples)
    print(f"Validation metrics: {metrics}")
    print(f"Estimates collected: {tokenizer.estimates}")
    
    # Manually trigger ratio updates (normally done after enough samples)
    tokenizer._update_ratios_from_estimates()
    
    # Print final ratios
    print(f"Final ratios: {tokenizer.token_ratios}")
    
    # Check that ratios were updated
    ratios_changed = False
    for text_type in initial_ratios:
        if text_type in tokenizer.token_ratios:
            # Print the before/after for each ratio
            print(f"{text_type}: {initial_ratios[text_type]} -> {tokenizer.token_ratios[text_type]}")
            if tokenizer.token_ratios[text_type] != initial_ratios[text_type]:
                ratios_changed = True
    
    # Assert that at least one ratio changed
    assert ratios_changed, "No token ratios were updated"
