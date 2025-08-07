"""Custom exceptions for the Qwen3-Coder Terminal Agent."""

class QwenAPIError(Exception):
    """Base exception for all Qwen API related errors."""
    pass

class AuthenticationError(QwenAPIError):
    """Raised when authentication with the API fails."""
    pass

class RateLimitError(QwenAPIError):
    """Raised when the rate limit is exceeded."""
    def __init__(self, message: str, retry_after: int = 5):
        super().__init__(message)
        self.retry_after = retry_after

class ContextLengthExceededError(QwenAPIError):
    """Raised when the context length is exceeded."""
    pass

class ContextLimitExceededError(QwenAPIError):
    """Raised when the context limit is exceeded during an operation."""
    pass

class TokenLimitExceededError(QwenAPIError):
    """Raised when the token limit is exceeded."""
    def __init__(self, message: str, max_tokens: int, requested_tokens: int):
        super().__init__(message)
        self.max_tokens = max_tokens
        self.requested_tokens = requested_tokens

class SessionError(QwenAPIError):
    """Raised when there's an error with the session management."""
    pass
