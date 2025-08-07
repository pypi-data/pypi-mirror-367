"""Token management for Qwen3-Coder interactions with hybrid counting."""
import time
from typing import List, Dict, Tuple, Optional, Union, Any

from .config import config
from .exceptions import TokenLimitExceededError
from .token_utils import tokenizer as qwen_tokenizer

class TokenManager:
    """Manages token counting and context window constraints with hybrid counting."""
    
    def __init__(self):
        # Track token usage
        self.total_tokens_used = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.validation_samples: List[Dict[str, Any]] = []
        
    def count_tokens(
        self, 
        text: str, 
        validate_with_api: bool = False,
        record_for_validation: bool = False
    ) -> int:
        """Count tokens in text using hybrid approach.
        
        Args:
            text: The text to count tokens for
            validate_with_api: If True, will verify with API and update ratios
            record_for_validation: If True, will record for later validation
            
        Returns:
            Estimated token count
        """
        return qwen_tokenizer.count_tokens(text, validate_with_api)
    
    def count_message_tokens(
        self, 
        messages: List[Dict[str, str]], 
        validate_with_api: bool = False
    ) -> int:
        """Count tokens for a list of messages in the chat format.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            validate_with_api: If True, will verify with API and update ratios
            
        Returns:
            Estimated token count for the messages
        """
        return qwen_tokenizer.count_message_tokens(messages)
    
    def check_context_limit(
        self, 
        messages: Union[List[Dict[str, str]], str],
        max_tokens: Optional[int] = None,
        validate_with_api: bool = False
    ) -> Tuple[bool, int, int]:
        """Check if adding a message would exceed the context window.
        
        Args:
            messages: List of messages or a single message string to check
            max_tokens: Maximum tokens allowed for the completion
            validate_with_api: If True, will verify with API and update ratios
            
        Returns:
            Tuple of (is_within_limit, total_tokens, available_tokens)
        """
        if max_tokens is None:
            max_tokens = config.MAX_TOKENS
            
        if isinstance(messages, str):
            total_tokens = self.count_tokens(messages, validate_with_api)
        else:
            total_tokens = self.count_message_tokens(messages, validate_with_api)
            
        available_tokens = config.MAX_CONTEXT_TOKENS - total_tokens - max_tokens
        
        if available_tokens < 0:
            return False, total_tokens, available_tokens
        return True, total_tokens, available_tokens
    
    def enforce_token_limit(
        self, 
        messages: List[Dict[str, str]], 
        max_tokens: int,
        validate_with_api: bool = False
    ) -> List[Dict[str, str]]:
        """Trim messages to fit within the token limit.
        
        Args:
            messages: List of messages to trim
            max_tokens: Maximum tokens allowed for the completion
            validate_with_api: If True, will verify with API and update ratios
            
        Returns:
            Trimmed list of messages that fits within the token limit
            
        Raises:
            TokenLimitExceededError: If even a single message exceeds the limit
        """
        # First check if any single message is too large
        max_allowed = config.MAX_CONTEXT_TOKENS - max_tokens
        for msg in messages:
            msg_tokens = self.count_tokens(msg.get('content', ''))
            if msg_tokens > max_allowed:
                raise TokenLimitExceededError(
                    f"Message is too large ({msg_tokens} tokens). "
                    f"Maximum allowed is {max_allowed} tokens.",
                    max_tokens=config.MAX_CONTEXT_TOKENS,
                    requested_tokens=msg_tokens + max_tokens
                )
        
        # If we're already under the limit, return as is
        within_limit, total_tokens, _ = self.check_context_limit(
            messages, max_tokens, validate_with_api
        )
        
        if within_limit:
            return messages
            
        # If we're over the limit, start removing older non-system messages
        trimmed_messages = messages.copy()
        
        # Keep system messages if present
        system_messages = [
            msg for msg in trimmed_messages 
            if msg.get("role") == "system"
        ]
        
        # Start with just system messages and add messages until we hit the limit
        trimmed_messages = system_messages.copy()
        remaining_messages = [
            msg for msg in messages 
            if msg.get("role") != "system"
        ]
        
        # Add messages from the end (most recent) until we hit the limit
        for msg in reversed(remaining_messages):
            # Create a new list with the current message added to the beginning
            test_messages = [msg] + trimmed_messages
            within_limit, total_tokens, _ = self.check_context_limit(
                test_messages, max_tokens, validate_with_api
            )
            
            if within_limit:
                # If we're still within limits, keep this message
                trimmed_messages = test_messages
            else:
                # If we've exceeded the limit, stop adding more messages
                break
                
        # If we couldn't fit any messages (besides system messages), keep at least the most recent message
        if len(trimmed_messages) == len(system_messages) and remaining_messages:
            trimmed_messages = [remaining_messages[-1]] + system_messages
                
        return trimmed_messages
    
    def update_usage(
        self, 
        usage: Dict[str, int],
        prompt_text: Optional[str] = None,
        completion_text: Optional[str] = None
    ) -> None:
        """Update token usage statistics and optionally validate token counts.
        
        Args:
            usage: Dictionary with 'prompt_tokens', 'completion_tokens', 'total_tokens'
            prompt_text: Optional prompt text for validation
            completion_text: Optional completion text for validation
        """
        # Update usage statistics
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        total_tokens = usage.get('total_tokens', 0)
        
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_tokens_used += total_tokens
        
        # If we have both prompt and completion text, validate the token counts
        if prompt_text is not None and completion_text is not None:
            self._validate_token_counts(
                prompt_text, 
                completion_text, 
                prompt_tokens, 
                completion_tokens
            )
    
    def _validate_token_counts(
        self,
        prompt_text: str,
        completion_text: str,
        actual_prompt_tokens: int,
        actual_completion_tokens: int
    ) -> None:
        """Validate token counts against actual API usage and update tokenizer.
        
        Args:
            prompt_text: The prompt text that was sent to the API
            completion_text: The completion text received from the API
            actual_prompt_tokens: Actual number of prompt tokens used
            actual_completion_tokens: Actual number of completion tokens used
        """
        # Skip validation if we don't have actual counts
        if actual_prompt_tokens <= 0 and actual_completion_tokens <= 0:
            return
            
        # Record the sample for batch validation
        self.validation_samples.append({
            'prompt': prompt_text,
            'completion': completion_text,
            'prompt_tokens': actual_prompt_tokens,
            'completion_tokens': actual_completion_tokens,
            'timestamp': time.time()
        })
        
        # Update the tokenizer with the latest samples
        if len(self.validation_samples) >= 5:  # Batch update every 5 samples
            self._update_tokenizer_ratios()
    
    def _update_tokenizer_ratios(self) -> None:
        """Update tokenizer ratios based on recent validation samples."""
        if not self.validation_samples:
            return
            
        # Prepare data for validation
        samples = self.validation_samples.copy()
        self.validation_samples = []  # Clear processed samples
        
        # Update tokenizer with actual counts
        for sample in samples:
            if sample['prompt_tokens'] > 0 and sample['prompt']:
                qwen_tokenizer.validate_accuracy([
                    (sample['prompt'], sample['prompt_tokens'])
                ])
                
            if sample['completion_tokens'] > 0 and sample['completion']:
                qwen_tokenizer.validate_accuracy([
                    (sample['completion'], sample['completion_tokens'])
                ])
    
    def get_usage_stats(self) -> Dict[str, int]:
        """Get current token usage statistics."""
        return {
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens_used,
        }
