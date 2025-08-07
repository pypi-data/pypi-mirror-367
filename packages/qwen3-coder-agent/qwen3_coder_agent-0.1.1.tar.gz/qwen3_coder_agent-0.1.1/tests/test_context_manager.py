"""Tests for context_manager.py"""
import os
import json
import tempfile
import shutil
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from qwen3_coder.context_manager import ContextManager, Message
from qwen3_coder.token_utils import QwenTokenizer

@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing persistence."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def context_manager(temp_dir):
    """Fixture providing a clean ContextManager instance for each test."""
    return ContextManager(
        max_tokens=1000,
        max_messages=10,
        tokenizer=QwenTokenizer(),
        persistence_dir=temp_dir
    )

def test_message_creation():
    """Test Message creation and serialization."""
    msg = Message(
        role="user",
        content="Hello, world!",
        name="test_user",
        function_call={"name": "test_func", "arguments": "{}"},
        token_count=5,
        timestamp=1234567890,
        metadata={"test": "value"}
    )
    
    # Test to_dict
    msg_dict = msg.to_dict()
    assert msg_dict["role"] == "user"
    assert msg_dict["content"] == "Hello, world!"
    assert msg_dict["name"] == "test_user"
    assert msg_dict["function_call"] == {"name": "test_func", "arguments": "{}"}
    
    # Test from_dict
    new_msg = Message.from_dict(msg_dict)
    assert new_msg.role == msg.role
    assert new_msg.content == msg.content
    assert new_msg.name == msg.name
    assert new_msg.function_call == msg.function_call
    # Note: token_count and metadata aren't included in to_dict output

def test_add_message(context_manager):
    """Test adding messages to the context."""
    msg = Message(role="user", content="Hello!")
    context_manager.add_message(msg)
    
    assert len(context_manager.messages) == 1
    assert context_manager._current_tokens > 0
    assert len(context_manager._message_hashes) == 1

def test_add_duplicate_message(context_manager):
    """Test that duplicate messages are not added."""
    msg1 = Message(role="user", content="Hello!")
    msg2 = Message(role="user", content="Hello!")  # Duplicate content
    
    context_manager.add_message(msg1)
    context_manager.add_message(msg2)
    
    assert len(context_manager.messages) == 1
    assert len(context_manager._message_hashes) == 1

def test_token_counting(context_manager):
    """Test that token counting works correctly."""
    # Mock the tokenizer to return predictable values
    with patch.object(context_manager.tokenizer, 'count_tokens', return_value=10):
        msg = Message(role="user", content="Test message")
        context_manager.add_message(msg)
        
        # Should have used our mocked token count
        assert context_manager._current_tokens > 0
        assert msg.token_count > 0

def test_summarization(context_manager):
    """Test conversation summarization."""
    # Add several messages to exceed the summary threshold
    for i in range(5):
        msg = Message(role="user" if i % 2 == 0 else "assistant", 
                     content=f"Message {i}")
        context_manager.add_message(msg)
    
    # Force summarization with a low token limit
    summary = context_manager.summarize(target_tokens=50)
    
    assert summary
    assert len(context_manager.messages) == 1  # Should be replaced with summary
    assert len(context_manager._summary_buffer) == 1
    assert context_manager.total_summaries_created == 1

def test_context_trimming(context_manager):
    """Test that the context is trimmed when limits are exceeded."""
    # Set a very low token limit
    context_manager.max_tokens = 10
    
    # Add a message that will exceed the limit
    msg = Message(role="user", content="This is a test message that is too long")
    context_manager.add_message(msg)
    
    # Should have triggered summarization
    assert len(context_manager.messages) == 1
    assert context_manager._current_tokens <= context_manager.max_tokens

def test_save_and_load_session(context_manager, temp_dir):
    """Test saving and loading a session."""
    # Add some messages
    for i in range(3):
        msg = Message(role="user" if i % 2 == 0 else "assistant", 
                     content=f"Message {i}")
        context_manager.add_message(msg)
    
    # Save the session
    session_id = context_manager.save_session("test_session")
    assert session_id == "test_session"
    
    # Create a new context manager and load the session
    new_cm = ContextManager(persistence_dir=temp_dir)
    assert new_cm.load_session("test_session") is True
    
    # Should have the same messages
    assert len(new_cm.messages) == len(context_manager.messages)
    for orig_msg, loaded_msg in zip(context_manager.messages, new_cm.messages):
        assert orig_msg.content == loaded_msg.content
        assert orig_msg.role == loaded_msg.role

def test_list_sessions(context_manager, temp_dir):
    """Test listing saved sessions."""
    # Create some test sessions
    for i in range(3):
        cm = ContextManager(persistence_dir=temp_dir)
        cm.add_message(Message(role="user", content=f"Test {i}"))
        cm.save_session(f"session_{i}")
    
    # List sessions
    sessions = context_manager.list_sessions()
    assert len(sessions) == 3
    assert all(s["session_id"].startswith("session_") for s in sessions)

def test_get_context_with_token_limit(context_manager, capsys):
    """Test getting context with a token limit."""
    # Add several messages with different token counts
    messages = [
        Message(role="system", content="System message"),
        Message(role="user", content="First message"),
        Message(role="assistant", content="First response"),
        Message(role="user", content="Second message"),
    ]
    
    # Mock the token counting to return specific values for our test
    token_counts = {
        "System message": 3,  # system message tokens
        "First message": 3,   # first user message tokens
        "First response": 4,  # assistant response tokens
        "Second message": 3   # second user message tokens
    }
    
    # Add debug output
    print("\n=== Test Setup ===")
    print(f"Messages to add (total: {len(messages)}):")
    for i, msg in enumerate(messages):
        print(f"  {i}: {msg.role.upper()} - '{msg.content}' (tokens: {token_counts.get(msg.content, '?')})")
    
    # Add messages with mocked token counts and set the token_count attribute directly
    for msg in messages:
        # Set the token count directly on the message
        msg.token_count = token_counts[msg.content]
        # Add the message to the context manager
        context_manager.messages.append(msg)
        # Update the token count in the context manager
        context_manager._current_tokens += msg.token_count
    
    # Print the current state of the context manager
    print("\n=== Context Manager State Before get_context ===")
    print(f"Total messages: {len(context_manager.messages)}")
    print(f"Current tokens: {context_manager._current_tokens}")
    for i, msg in enumerate(context_manager.messages):
        print(f"  {i}: {msg.role.upper()} - '{msg.content}' (tokens: {msg.token_count})")
    
    # Set a token limit that only allows the system message and the most recent user message
    # system (3) + second message (3) = 6 tokens
    # This is less than system + first message + assistant + second message (3+3+4+3=13)
    token_limit = 10
    print(f"\n=== Calling get_context(max_tokens={token_limit}) ===")
    context = context_manager.get_context(max_tokens=token_limit)
    
    # Print the resulting context
    print("\n=== Resulting Context ===")
    print(f"Number of messages: {len(context)}")
    for i, msg in enumerate(context):
        print(f"  {i}: {msg['role'].upper()} - '{msg['content']}'")
    
    # Should include system message and most recent user message
    assert len(context) == 2, f"Expected 2 messages but got {len(context)}: {context}"
    assert context[0]["role"] == "system", f"First message should be system, got {context[0]['role']}"
    assert context[1]["role"] == "user", f"Second message should be user, got {context[1]['role']}"
    assert context[1]["content"] == "Second message", "Should include the most recent user message"
    assert context[1]["content"] == "Second message"

def test_enforce_limits_with_summary_threshold():
    """Test that summarization is triggered when the threshold is reached."""
    # Create a context manager with a low summary threshold
    cm = ContextManager(max_tokens=100, summary_threshold=0.5)
    
    # Mock the tokenizer to return a fixed token count
    with patch.object(cm.tokenizer, 'count_tokens', return_value=20) as mock_count_tokens:
        # Mock the summarization method
        with patch.object(cm, 'summarize') as mock_summarize:
            # Add messages until we hit the threshold
            for i in range(5):
                # Create message with content and explicitly set token count
                msg = Message(role="user", content=f"Message {i}")
                msg.token_count = 20  # Each message is 20 tokens
                
                # Add message and update token count manually since we're mocking the tokenizer
                cm.messages.append(msg)
                cm._current_tokens += msg.token_count
                cm._message_hashes.add(cm._hash_message(msg))
                cm.total_messages_processed += 1
                cm.total_tokens_processed += msg.token_count
                
                # After adding enough messages, summarization should be triggered
                if i >= 2:  # 60 tokens / 100 max = 60% > 50% threshold
                    # Call _enforce_limits directly to trigger summarization
                    cm._enforce_limits()
                    mock_summarize.assert_called_once()
                    mock_summarize.reset_mock()  # Reset for next iteration

def test_message_metadata(context_manager):
    """Test that message metadata is preserved."""
    metadata = {"source": "test", "priority": 1}
    msg = Message(role="user", content="Test message", metadata=metadata)
    context_manager.add_message(msg)
    
    assert context_manager.messages[0].metadata == metadata
    
    # Test serialization round-trip
    session_id = context_manager.save_session("metadata_test")
    new_cm = ContextManager(persistence_dir=context_manager.persistence_dir)
    new_cm.load_session(session_id)
    
    assert new_cm.messages[0].metadata == metadata

def test_clear_context(context_manager):
    """Test clearing the context."""
    # Add some messages
    for i in range(3):
        msg = Message(role="user", content=f"Message {i}")
        context_manager.add_message(msg)
    
    # Clear the context
    context_manager.clear()
    
    # Should be empty
    assert len(context_manager.messages) == 0
    assert context_manager._current_tokens == 0
    assert len(context_manager._message_hashes) == 0
    assert len(context_manager._summary_buffer) == 0

def test_statistics_tracking(context_manager):
    """Test that usage statistics are tracked correctly."""
    # Initial stats
    stats = context_manager.get_statistics()
    assert stats["current_messages"] == 0
    assert stats["current_tokens"] == 0
    assert stats["total_messages_processed"] == 0
    assert stats["total_tokens_processed"] == 0
    
    # Add some messages
    for i in range(3):
        msg = Message(role="user", content=f"Message {i}")
        context_manager.add_message(msg)
    
    # Check updated stats
    stats = context_manager.get_statistics()
    assert stats["current_messages"] == 3
    assert stats["current_tokens"] > 0
    assert stats["total_messages_processed"] == 3
    assert stats["total_tokens_processed"] > 0
    assert stats["total_summaries_created"] == 0
    
    # Force summarization
    context_manager.summarize(target_tokens=10)
    
    # Check stats after summarization
    stats = context_manager.get_statistics()
    assert stats["current_messages"] == 1  # Replaced with summary
    assert stats["total_summaries_created"] == 1
    assert stats["total_tokens_saved"] > 0  # Should have saved some tokens
