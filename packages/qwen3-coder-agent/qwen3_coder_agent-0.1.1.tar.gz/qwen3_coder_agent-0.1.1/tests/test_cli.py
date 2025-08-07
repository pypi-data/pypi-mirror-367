"""Tests for the Qwen3-Coder CLI."""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
from pathlib import Path

from qwen3_coder.cli import QwenCoderCLI
from qwen3_coder.context_manager import ContextManager, Message
from qwen3_coder.api_client import QwenAPIClient
from qwen3_coder.token_manager import TokenManager

@pytest.fixture
def mock_components():
    """Create mock components for testing the CLI."""
    with patch('qwen3_coder.token_utils.QwenTokenizer'), \
         patch('qwen3_coder.cli.TokenManager') as mock_tm, \
         patch('qwen3_coder.cli.RateLimiter') as mock_rl, \
         patch('qwen3_coder.cli.ContextManager') as mock_cm, \
         patch('qwen3_coder.cli.QwenAPIClient') as mock_api:
        
        # Set up mock return values
        mock_tm.return_value = MagicMock(spec=TokenManager)
        mock_rl.return_value = MagicMock()
        mock_cm.return_value = MagicMock(spec=ContextManager)
        mock_api.return_value = MagicMock(spec=QwenAPIClient)
        
        # Create a CLI instance with mocks
        cli = QwenCoderCLI()
        
        # Configure mocks
        cli.context.get_statistics.return_value = {
            'current_tokens': 100,
            'max_tokens': 4000,
            'token_usage_pct': 2.5,
            'current_messages': 3,
            'total_messages_processed': 10,
            'total_tokens_processed': 5000,
            'total_tokens_saved': 1000,
            'total_summaries_created': 2
        }
        
        # Add stream_chat_completion method to the mock API client
        cli.api_client.stream_chat_completion = MagicMock()
        
        cli.context.list_sessions.return_value = [
            {
                'session_id': 'sess_123',
                'name': 'test_session',
                'timestamp': 1620000000,
                'message_count': 5
            }
        ]
        
        yield cli, mock_tm, mock_rl, mock_cm, mock_api

@pytest.fixture
def cli_runner(mock_components):
    """Create a CLI test runner."""
    cli, *_ = mock_components
    
    def run_commands(commands, expected_output=None):
        """Run CLI commands and capture output."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            for cmd in commands:
                cli.onecmd(cmd)
            output = fake_out.getvalue()
            
        if expected_output:
            if isinstance(expected_output, str):
                assert expected_output in output
            else:
                for exp in expected_output:
                    assert exp in output
        
        return output
    
    return run_commands, cli

def test_cli_help(cli_runner):
    """Test the help command."""
    run, _ = cli_runner
    output = run(["help"])
    
    assert "Available commands" in output
    assert "help" in output
    assert "exit" in output

def test_cli_exit(cli_runner):
    """Test the exit command."""
    run, cli = cli_runner
    
    # Should return True to exit the cmdloop
    assert cli.do_exit("") is True
    
    # Should set running to False
    cli.running = True
    run(["exit"])
    assert cli.running is False

def test_cli_clear(cli_runner):
    """Test the clear command."""
    run, cli = cli_runner
    
    run(["clear"])
    cli.context.clear.assert_called_once()

def test_cli_tokens(cli_runner):
    """Test the tokens command."""
    run, _ = cli_runner
    
    output = run(["tokens"])
    
    assert "Token Usage" in output
    assert "Current context: 100 tokens" in output
    assert "Context limit:   4,000 tokens" in output
    assert "Usage:           2.5% of limit" in output

def test_cli_sessions_list(cli_runner):
    """Test listing sessions."""
    run, cli = cli_runner
    
    output = run(["sessions"])
    
    assert "test_session" in output
    assert "5" in output  # message count

def test_cli_save_session(cli_runner):
    """Test saving a session."""
    run, cli = cli_runner
    
    # Test with custom name
    run(["save test_session"])
    cli.context.save_session.assert_called_with("test_session")
    
    # Test with auto-generated name
    with patch('time.time', return_value=1234567890):
        run(["save"])
        cli.context.save_session.assert_called_with("session_1234567890")

def test_cli_load_session(cli_runner):
    """Test loading a session."""
    run, cli = cli_runner
    
    # Mock successful load
    cli.context.load_session.return_value = True
    
    run(["load test_session"])
    cli.context.load_session.assert_called_with("test_session")
    assert cli.current_session == "test_session"

def test_cli_load_session_not_found(cli_runner):
    """Test loading a non-existent session."""
    run, cli = cli_runner
    
    # Mock failed load
    cli.context.load_session.return_value = False
    
    output = run(["load non_existent"])
    assert "Session not found" in output

def test_cli_chat_message(cli_runner):
    """Test sending a chat message."""
    run, cli = cli_runner
    
    # Mock the API response
    cli.api_client.stream_chat_completion.return_value = ["Hello", " there"]
    
    output = run(["Hello, how are you?"])
    
    # Check that the message was added to context
    cli.context.add_message.assert_called()
    
    # Check that the response was printed
    assert "Hello there" in output

def test_cli_unknown_command(cli_runner):
    """Test handling of unknown commands."""
    run, _ = cli_runner
    
    output = run(["/nonexistent"], "Unknown command: nonexistent")
    assert "Unknown command" in output

def test_cli_command_aliases(cli_runner):
    """Test command aliases."""
    run, cli = cli_runner
    
    # Test '?' alias for help
    run(["?"], "Available commands")
    
    # Test 'q' alias for exit
    cli.running = True
    run(["q"])
    assert cli.running is False
    
    # Test 'l' alias for load
    cli.context.load_session.return_value = True
    run(["l test_session"])
    cli.context.load_session.assert_called_with("test_session")
    
    # Test 'ls' alias for sessions
    run(["ls"], "test_session")

def test_cli_main_function():
    """Test the main entry point."""
    with patch('qwen3_coder.cli.QwenCoderCLI') as mock_cls, \
         patch('sys.argv', ['qwen3-coder']):
        
        # Mock the cmdloop method
        mock_instance = mock_cls.return_value
        mock_instance.cmdloop.return_value = None
        
        # Import and run the main function
        from qwen3_coder.cli import main
        main()
        
        # Check that the CLI was instantiated and cmdloop was called
        mock_cls.assert_called_once()
        mock_instance.cmdloop.assert_called_once()

def test_cli_streaming_response(cli_runner):
    """Test handling of streaming responses."""
    run, cli = cli_runner
    
    # Mock the streaming response as a sync generator
    def mock_stream():
        yield "Hello"
        yield " there"
        yield "!"
    
    cli.api_client.stream_chat_completion.return_value = mock_stream()
    
    # Test sending a message
    output = run(["Hello"], "Hello there!")
    
    # Check that the response was streamed
    assert "Hello there!" in output
