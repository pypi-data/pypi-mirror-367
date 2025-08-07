"""Adaptive rate limiting for Qwen3 API requests."""
import asyncio
import time
from collections import deque
from typing import Dict, List, Optional, Tuple, Deque
import math

from .config import config
from .exceptions import RateLimitError

class RateLimiter:
    """Implements adaptive rate limiting with token and request tracking.
    
    This class tracks both request counts and token usage over sliding time windows
    to ensure we stay within Qwen3 API rate limits while maximizing throughput.
    """
    
    def __init__(self):
        # Request tracking (for RPM limits)
        self.request_timestamps: Deque[float] = deque()
        
        # Token usage tracking (for TPM limits)
        self.token_windows: Dict[str, Deque[Tuple[float, int]]] = {
            'input': deque(),
            'output': deque()
        }
        
        # Rate limit configuration (requests per minute and tokens per minute)
        self.rpm_limit = 60  # Default, will be updated from config
        self.tpm_limits = {
            'input': 90000,   # Default input tokens per minute
            'output': 30000   # Default output tokens per minute
        }
        
        # Adaptive rate limiting parameters
        self.safety_margin = 0.8  # Stay below 80% of limits
        self.min_wait_time = 0.1  # Minimum wait time between requests (seconds)
        self.last_request_time = 0
        
        # Statistics
        self.total_requests = 0
        self.total_tokens = {'input': 0, 'output': 0}
        self.rate_limit_hits = 0
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load rate limiting configuration from environment."""
        # These would ideally come from config or be discovered from API
        self.rpm_limit = getattr(config, 'RPM_LIMIT', 60)
        self.tpm_limits['input'] = getattr(config, 'TPM_INPUT_LIMIT', 90000)
        self.tpm_limits['output'] = getattr(config, 'TPM_OUTPUT_LIMIT', 30000)
    
    def update_limits(self, headers: Optional[Dict[str, str]] = None) -> None:
        """Update rate limits from API response headers.
        
        Args:
            headers: Response headers from Qwen3 API
        """
        if not headers:
            return
            
        # Update RPM limit if provided in headers
        if 'X-RateLimit-Limit-RPM' in headers:
            try:
                self.rpm_limit = int(headers['X-RateLimit-Limit-RPM'])
            except (ValueError, TypeError):
                pass
                
        # Update TPM limits if provided in headers
        for token_type in ['input', 'output']:
            header_key = f'X-RateLimit-Limit-TPM-{token_type.upper()}'
            if header_key in headers:
                try:
                    self.tpm_limits[token_type] = int(headers[header_key])
                except (ValueError, TypeError):
                    pass
    
    def _prune_old_requests(self, window_seconds: int = 60) -> None:
        """Remove old requests from tracking that are outside the time window."""
        current_time = time.time()
        
        # Prune request timestamps
        while (self.request_timestamps and 
               current_time - self.request_timestamps[0] > window_seconds):
            self.request_timestamps.popleft()
        
        # Prune token usage
        for token_type in self.token_windows:
            while (self.token_windows[token_type] and 
                   current_time - self.token_windows[token_type][0][0] > window_seconds):
                self.token_windows[token_type].popleft()
    
    def get_current_usage(self) -> Dict[str, float]:
        """Get current usage statistics.
        
        Returns:
            Dictionary with current usage metrics:
            - rpm: Current requests per minute
            - tpm_input: Current input tokens per minute
            - tpm_output: Current output tokens per minute
            - rpm_pct: Percentage of RPM limit used
            - tpm_input_pct: Percentage of input TPM limit used
            - tpm_output_pct: Percentage of output TPM limit used
        """
        self._prune_old_requests()
        
        current_time = time.time()
        
        # Calculate RPM (requests per minute)
        rpm = len(self.request_timestamps)
        rpm_pct = (rpm / max(1, self.rpm_limit)) * 100
        
        # Calculate TPM (tokens per minute) for input and output
        tpm = {}
        tpm_pct = {}
        
        for token_type in self.token_windows:
            tpm[token_type] = sum(
                tokens for _, tokens in self.token_windows[token_type]
            )
            tpm_pct[token_type] = (
                tpm[token_type] / max(1, self.tpm_limits[token_type])
            ) * 100
        
        return {
            'rpm': rpm,
            'tpm_input': tpm.get('input', 0),
            'tpm_output': tpm.get('output', 0),
            'rpm_pct': rpm_pct,
            'tpm_input_pct': tpm_pct.get('input', 0),
            'tpm_output_pct': tpm_pct.get('output', 0)
        }
    
    def record_request(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        """Record a completed API request and its token usage.
        
        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
        """
        current_time = time.time()
        
        # Record the request
        self.request_timestamps.append(current_time)
        self.total_requests += 1
        
        # Record token usage
        if input_tokens > 0:
            self.token_windows['input'].append((current_time, input_tokens))
            self.total_tokens['input'] += input_tokens
            
        if output_tokens > 0:
            self.token_windows['output'].append((current_time, output_tokens))
            self.total_tokens['output'] += output_tokens
        
        # Update last request time
        self.last_request_time = current_time
        
        # Clean up old entries
        self._prune_old_requests()
    
    def calculate_wait_time(
        self, 
        expected_input_tokens: int = 0, 
        expected_output_tokens: int = 0
    ) -> float:
        """Calculate how long to wait before making the next request.
        
        Args:
            expected_input_tokens: Expected number of input tokens for next request
            expected_output_tokens: Expected number of output tokens for next request
            
        Returns:
            Number of seconds to wait before making the next request
        """
        current_time = time.time()
        self._prune_old_requests()
        
        # Calculate current usage
        usage = self.get_current_usage()
        
        # Calculate time until we're under the safety margin for RPM
        rpm_wait_time = 0.0
        if usage['rpm'] >= self.rpm_limit * self.safety_margin:
            # Calculate when the oldest request will fall out of the window
            if self.request_timestamps:
                oldest_request = self.request_timestamps[0]
                time_since_oldest = current_time - oldest_request
                rpm_wait_time = max(0, 60 - time_since_oldest)  # Wait until window slides
        
        # Calculate time until we're under the safety margin for TPM
        tpm_wait_time = 0.0
        
        # Check input tokens
        if (usage['tpm_input'] + expected_input_tokens > 
                self.tpm_limits['input'] * self.safety_margin):
            if self.token_windows['input']:
                oldest_input = self.token_windows['input'][0][0]
                time_since_oldest = current_time - oldest_input
                tpm_wait_time = max(tpm_wait_time, 60 - time_since_oldest)
        
        # Check output tokens
        if (usage['tpm_output'] + expected_output_tokens > 
                self.tpm_limits['output'] * self.safety_margin):
            if self.token_windows['output']:
                oldest_output = self.token_windows['output'][0][0]
                time_since_oldest = current_time - oldest_output
                tpm_wait_time = max(tpm_wait_time, 60 - time_since_oldest)
        
        # Calculate minimum time between requests
        min_interval_wait = 0.0
        if self.last_request_time > 0:
            time_since_last = current_time - self.last_request_time
            min_interval_wait = max(0, self.min_wait_time - time_since_last)
        
        # Return the maximum wait time needed
        return max(rpm_wait_time, tpm_wait_time, min_interval_wait)
    
    async def wait_if_needed(
        self, 
        expected_input_tokens: int = 0, 
        expected_output_tokens: int = 0
    ) -> None:
        """Wait if needed to stay within rate limits.
        
        Args:
            expected_input_tokens: Expected number of input tokens for next request
            expected_output_tokens: Expected number of output tokens for next request
        """
        wait_time = self.calculate_wait_time(expected_input_tokens, expected_output_tokens)
        if wait_time > 0:
            self.rate_limit_hits += 1
            await asyncio.sleep(wait_time)
    
    def check_rate_limit(
        self,
        expected_input_tokens: int = 0,
        expected_output_tokens: int = 0
    ) -> None:
        """Check if a request would exceed rate limits.
        
        Args:
            expected_input_tokens: Expected number of input tokens
            expected_output_tokens: Expected number of output tokens
            
        Raises:
            RateLimitError: If the request would exceed rate limits
        """
        current_time = time.time()
        self._prune_old_requests()
        
        # Check RPM limit
        if len(self.request_timestamps) >= self.rpm_limit:
            raise RateLimitError(
                f"Rate limit exceeded: {len(self.request_timestamps)}/{self.rpm_limit} RPM",
                retry_after=60 - (current_time - self.request_timestamps[0])
            )
        
        # Check TPM limits
        for token_type, expected_tokens in [
            ('input', expected_input_tokens),
            ('output', expected_output_tokens)
        ]:
            if expected_tokens <= 0:
                continue
                
            current_tokens = sum(
                tokens for _, tokens in self.token_windows[token_type]
            )
            
            if current_tokens + expected_tokens > self.tpm_limits[token_type]:
                # Calculate when we can make the next request
                if self.token_windows[token_type]:
                    retry_after = 60 - (current_time - self.token_windows[token_type][0][0])
                else:
                    retry_after = 60  # Default to 1 minute if no history
                
                raise RateLimitError(
                    f"{token_type.capitalize()} token limit exceeded: "
                    f"{current_tokens + expected_tokens}/{self.tpm_limits[token_type]} TPM",
                    retry_after=retry_after
                )
    
    def get_stats(self) -> Dict[str, float]:
        """Get rate limiting statistics.
        
        Returns:
            Dictionary with rate limiting statistics
        """
        usage = self.get_current_usage()
        
        return {
            'total_requests': self.total_requests,
            'total_input_tokens': self.total_tokens['input'],
            'total_output_tokens': self.total_tokens['output'],
            'current_rpm': usage['rpm'],
            'current_tpm_input': usage['tpm_input'],
            'current_tpm_output': usage['tpm_output'],
            'rpm_limit': self.rpm_limit,
            'tpm_input_limit': self.tpm_limits['input'],
            'tpm_output_limit': self.tpm_limits['output'],
            'rate_limit_hits': self.rate_limit_hits
        }
