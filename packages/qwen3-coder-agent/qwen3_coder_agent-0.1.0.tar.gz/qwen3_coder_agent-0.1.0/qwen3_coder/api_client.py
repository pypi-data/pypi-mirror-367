"""API client for Qwen3 with rate limiting and retry logic."""
import json
import time
from typing import Dict, List, Optional, Any, Union
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    RetryCallState,
)

from .config import config
from .exceptions import (
    QwenAPIError,
    RateLimitError,
    AuthenticationError,
    ContextLengthExceededError,
)

class QwenAPIClient:
    """Client for interacting with the Qwen3 API with rate limiting and retries."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the API client.
        
        Args:
            api_key: Optional API key. If not provided, will use the one from config.
        """
        self.api_key = api_key or config.QWEN_API_KEY
        self.base_url = config.API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        })
        
        # Track rate limits
        self.rate_limit_remaining = 60  # Default, will be updated from headers
        self.rate_limit_reset = 0

    def _handle_rate_limit(self, response: requests.Response) -> None:
        """Update rate limit tracking from response headers."""
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        if 'X-RateLimit-Reset' in response.headers:
            self.rate_limit_reset = int(response.headers['X-RateLimit-Reset'])

    def _should_retry(self, response: requests.Response) -> bool:
        """Determine if a request should be retried based on the response."""
        if response.status_code == 429:  # Too Many Requests
            return True
        if response.status_code >= 500:  # Server errors
            return True
        return False

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make an API request with retry logic."""
        @retry(
            stop=stop_after_attempt(config.MAX_RETRIES),
            wait=wait_exponential(
                multiplier=1,
                min=config.INITIAL_RETRY_DELAY,
                max=config.MAX_RETRY_DELAY,
            ),
            retry=retry_if_exception_type((RateLimitError, requests.RequestException)),
            before_sleep=self._log_retry_attempt,
        )
        def _make_retryable_request():
            response = self.session.post(
                self.base_url,
                json=payload,
                timeout=30,  # 30 second timeout
            )
            
            # Update rate limit tracking
            self._handle_rate_limit(response)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                raise RateLimitError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds.",
                    retry_after=retry_after,
                )
                
            # Handle other errors
            response.raise_for_status()
            
            return response.json()
            
        try:
            return _make_retryable_request()
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 401:
                raise AuthenticationError("Invalid API key") from http_err
            if http_err.response.status_code == 400 and "context_length" in str(http_err).lower():
                raise ContextLengthExceededError("Context length exceeded") from http_err
            raise QwenAPIError(f"HTTP error occurred: {http_err}") from http_err
            
        except requests.exceptions.RequestException as req_err:
            raise QwenAPIError(f"Request failed: {req_err}") from req_err

    def _log_retry_attempt(self, retry_state: RetryCallState) -> None:
        """Log retry attempts with exponential backoff."""
        if retry_state.outcome is None:
            return
            
        exception = retry_state.outcome.exception()
        wait_time = getattr(exception, 'retry_after', None)
        
        if wait_time is None:
            wait_time = min(
                config.INITIAL_RETRY_DELAY * (2 ** (retry_state.attempt_number - 1)),
                config.MAX_RETRY_DELAY
            )
            
        print(f"Retrying in {wait_time:.1f} seconds... (Attempt {retry_state.attempt_number}/{config.MAX_RETRIES})")
        time.sleep(wait_time)

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Generate a chat completion using the Qwen3 model.
        
        Args:
            messages: List of message dicts with 'role' and 'content'.
            model: Model name to use. Defaults to the one in config.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            stream: Whether to stream the response.
            
        Returns:
            The API response as a dictionary.
        """
        payload = {
            "model": model or config.MODEL_NAME,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }
        
        if max_tokens is not None:
            payload["max_tokens"] = min(max_tokens, config.MAX_TOKENS)
        
        return self._make_request(payload)
