# Qwen3-Coder Terminal Agent

A powerful terminal interface for interacting with the Qwen3-Coder model, featuring secure API key management, hybrid token counting, and intelligent rate limiting.

## Features

- **Hybrid Token Counting**: Combines local estimation with API validation for accurate token counting
- **Secure API Key Management**: Environment-based configuration with secure storage
- **Adaptive Rate Limiting**: Intelligent handling of rate limits with predictive throttling
- **Context Management**: Dynamic windowing for large conversations
- **Terminal UX**: Clean interface with real-time token usage
- **Session Persistence**: Save and load conversation history

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/qwen3-coder-terminal.git
   cd qwen3-coder-terminal
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API configuration:
   ```env
   QWEN_API_KEY=your_api_key_here
   QWEN_API_BASE=https://api.qwen.com/v1  # Default value, update if different
   MAX_CONTEXT_TOKENS=4000  # Adjust based on your model's context window
   ```

## Usage

Start the terminal interface:
```bash
python -m qwen3_coder.cli
```

### Available Commands

#### Chat Commands
- Just type your message and press Enter to chat with Qwen3-Coder
- Multi-line input is supported (press Shift+Enter for new lines, Enter to send)

#### System Commands
- `/help` or `?` - Show help message with available commands
- `/exit` or `/q` - Exit the application
- `/clear` - Clear the current conversation
- `/tokens` or `/t` - Show token usage statistics

#### Session Management
- `/save [name]` or `/s [name]` - Save current conversation
- `/load <id>` or `/l <id>` - Load a saved session
- `/sessions` or `/ls` - List all saved sessions

## Configuration

The following environment variables can be set in the `.env` file:

- `QWEN_API_KEY`: Your Qwen API key (required)
- `QWEN_API_BASE`: Base URL for the Qwen API (default: `https://api.qwen.com/v1`)
- `MAX_CONTEXT_TOKENS`: Maximum number of tokens to keep in context (default: 4000)

## Examples

### Starting a new conversation
```
qwen3> Hello! How can I help you today?
```

### Saving a session
```
qwen3> /save my_first_session
Session saved as: my_first_session
```

### Loading a session
```
qwen3> /load my_first_session
Session loaded: my_first_session
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
This project uses `black` for code formatting and `flake8` for linting.

```bash
black .
flake8
```

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
- `/save [name]` - Save current session
- `/load <name>` - Load a saved session
- `/model [name]` - Get or set the current model
- `/debug` - Toggle debug mode
- `/new` - Start a new session
- `/system <msg>` - Add a system message
- `/settings` - Show current settings
- `/exit` or `/quit` - Exit the program

## Configuration

Edit the `.env` file to customize settings:

```env
# API Configuration
QWEN_API_KEY=your_api_key_here
API_BASE_URL=https://api.qwen.ai/v1/chat/completions

# Rate Limiting
MAX_RETRIES=3
INITIAL_RETRY_DELAY=1
MAX_RETRY_DELAY=10

# Token Management
MAX_TOKENS=4096
MAX_CONTEXT_TOKENS=32000
WARNING_THRESHOLD=0.8
```

## Security

- API keys are never logged or stored in plaintext
- Environment variables are used for configuration
- Secure credential storage options available via keyring
- All API calls use HTTPS

## Development

1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Format code:
   ```bash
   black .
   isort .
   ```

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Acknowledgements

- [Qwen Team](https://github.com/Qwen) for the Qwen3-Coder model
- [OpenAI](https://openai.com) for the tiktoken library
- [Python Prompt Toolkit](https://python-prompt-toolkit.readthedocs.io/) for the terminal interface
