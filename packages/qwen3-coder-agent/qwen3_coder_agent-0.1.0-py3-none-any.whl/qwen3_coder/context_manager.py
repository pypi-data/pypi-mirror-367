"""Context management for Qwen3-Coder conversations."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Deque, Any
from collections import deque
import json
import time
import re
import hashlib
from pathlib import Path

from .token_utils import QwenTokenizer
from .exceptions import ContextLimitExceededError
from .config import config

@dataclass
class Message:
    """Represents a single message in the conversation."""
    role: str  # 'system', 'user', 'assistant', or 'function'
    content: str
    name: Optional[str] = None  # For function calls
    function_call: Optional[Dict] = None
    token_count: int = 0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary format for API."""
        result = {
            'role': self.role,
            'content': self.content,
        }
        if self.name:
            result['name'] = self.name
        if self.function_call:
            result['function_call'] = self.function_call
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        """Create a Message from a dictionary."""
        return cls(
            role=data['role'],
            content=data.get('content', ''),
            name=data.get('name'),
            function_call=data.get('function_call'),
            token_count=data.get('token_count', 0),
            timestamp=data.get('timestamp', time.time()),
            metadata=data.get('metadata', {})
        )

class ContextManager:
    """Manages conversation context with dynamic windowing and summarization."""
    
    def __init__(
        self,
        max_tokens: int = 32000,
        max_messages: int = 100,
        tokenizer: Optional[QwenTokenizer] = None,
        summary_threshold: float = 0.8,  # Summarize when context reaches 80% of max
        summary_ratio: float = 0.5,     # Target 50% reduction in tokens when summarizing
        persistence_dir: Optional[str] = None
    ):
        """Initialize the context manager.
        
        Args:
            max_tokens: Maximum number of tokens to keep in context
            max_messages: Maximum number of messages to keep in context
            tokenizer: Tokenizer instance (will create one if not provided)
            summary_threshold: Fraction of max_tokens at which to trigger summarization
            summary_ratio: Target reduction in token count when summarizing
            persistence_dir: Directory for saving/loading conversation states
        """
        self.max_tokens = max_tokens
        self.max_messages = max_messages
        self.summary_threshold = summary_threshold
        self.summary_ratio = summary_ratio
        self.tokenizer = tokenizer or QwenTokenizer()
        self.persistence_dir = Path(persistence_dir or "./sessions")
        self.persistence_dir.mkdir(exist_ok=True, parents=True)
        
        # Conversation state
        self.messages: List[Message] = []
        self._current_tokens = 0
        self._message_hashes = set()  # For deduplication
        self._summary_buffer: List[str] = []  # Stores summaries of condensed messages
        self._conversation_id: Optional[str] = None
        
        # Statistics
        self.total_tokens_processed = 0
        self.total_messages_processed = 0
        self.total_summaries_created = 0
        self.total_tokens_saved = 0
    
    def add_message(self, message: Message, recalculate_tokens: bool = False) -> None:
        """Add a message to the context.
        
        Args:
            message: The message to add
            recalculate_tokens: If True, force recalculation of token counts
        """
        # Skip empty messages
        if not message.content and not message.function_call:
            return
            
        # Calculate token count if not provided or if forced
        if recalculate_tokens or message.token_count == 0:
            message.token_count = self._count_message_tokens(message)
        
        # Check for duplicates
        message_hash = self._hash_message(message)
        if message_hash in self._message_hashes:
            return
        
        # Add message and update state
        self.messages.append(message)
        self._current_tokens += message.token_count
        self._message_hashes.add(message_hash)
        self.total_messages_processed += 1
        self.total_tokens_processed += message.token_count
        
        # Ensure we're not over limits
        self._enforce_limits()
    
    def add_messages(self, messages: List[Message]) -> None:
        """Add multiple messages to the context."""
        for msg in messages:
            self.add_message(msg)
    
    def get_context(self, max_tokens: Optional[int] = None) -> List[Dict]:
        """Get the current conversation context as a list of message dictionaries.
        
        Args:
            max_tokens: Optional maximum tokens for the returned context
            
        Returns:
            List of message dictionaries suitable for the API
        """
        import logging
        import sys
        
        # Set up logging to print to stdout for test visibility
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            stream=sys.stdout
        )
        logger = logging.getLogger('context_manager')
        
        # If no max_tokens specified or we're under the limit, return all messages
        if not max_tokens or max_tokens >= self._current_tokens:
            logger.debug("No token limit or under limit, returning all messages")
            return [msg.to_dict() for msg in self.messages]
            
        logger.debug(f"\n=== get_context(max_tokens={max_tokens}) ===")
        logger.debug(f"Current token count: {self._current_tokens}")
        
        # Log all messages with their token counts
        logger.debug("All messages in context:")
        for i, msg in enumerate(self.messages):
            logger.debug(f"  {i}: {msg.role.upper()} - '{msg.content}' (tokens: {msg.token_count})")
        
        # Separate system and non-system messages
        system_messages = [msg for msg in self.messages if msg.role == 'system']
        non_system_messages = [msg for msg in self.messages if msg.role != 'system']
        
        # Calculate system message tokens
        sys_tokens = sum(msg.token_count for msg in system_messages) if system_messages else 0
        logger.debug(f"\nSystem messages: {len(system_messages)} messages, {sys_tokens} tokens")
        
        # If system messages alone exceed the limit, just return the most recent one
        if sys_tokens > max_tokens:
            logger.debug("System messages exceed token limit, returning only the most recent system message")
            return [system_messages[-1].to_dict()] if system_messages else []
        
        # Start with system messages if they fit
        included_messages = system_messages.copy()
        total_tokens = sys_tokens
        logger.debug(f"Included system messages: {len(included_messages)} messages, {total_tokens} tokens")
        
        # We'll try to include the most recent user message and its response if possible
        # First, find the most recent user message that would fit with system messages
        recent_user_msg = None
        logger.debug("\nSearching for most recent user message that fits:")
        
        for i, msg in enumerate(reversed(non_system_messages)):
            logger.debug(f"  Checking message {len(non_system_messages)-i-1}: {msg.role.upper()} - '{msg.content}' ({msg.token_count} tokens)")
            if msg.role == 'user':
                if (total_tokens + msg.token_count) <= max_tokens:
                    recent_user_msg = msg
                    logger.debug(f"  ✓ Found user message that fits: '{msg.content}' ({msg.token_count} tokens)")
                    break
                else:
                    logger.debug(f"  ✗ User message too large: {total_tokens} + {msg.token_count} > {max_tokens}")
        
        # If we found a user message that fits, add it
        if recent_user_msg:
            logger.debug(f"\nIncluding user message: '{recent_user_msg.content}' ({recent_user_msg.token_count} tokens)")
            included_messages.append(recent_user_msg)
            total_tokens += recent_user_msg.token_count
            logger.debug(f"Total tokens after adding user message: {total_tokens}")
            
            # Now try to include the assistant's response to this message if it exists and fits
            msg_idx = non_system_messages.index(recent_user_msg)
            if msg_idx + 1 < len(non_system_messages):
                next_msg = non_system_messages[msg_idx + 1]
                if next_msg.role == 'assistant':
                    if (total_tokens + next_msg.token_count) <= max_tokens:
                        logger.debug(f"Including assistant response: '{next_msg.content}' ({next_msg.token_count} tokens)")
                        included_messages.append(next_msg)
                        total_tokens += next_msg.token_count
                        logger.debug(f"Total tokens after adding assistant response: {total_tokens}")
                    else:
                        logger.debug(f"Skipping assistant response - would exceed token limit: {total_tokens} + {next_msg.token_count} > {max_tokens}")
        else:
            logger.debug("No user messages could be included within token limit")
        
        # If we couldn't include any non-system messages and there are system messages, return them
        if not recent_user_msg and system_messages:
            logger.debug("\nNo user messages fit, returning only system messages")
            return [msg.to_dict() for msg in system_messages]
            
        # If we have no messages at all, return the most recent message (even if it exceeds the limit)
        if not included_messages and non_system_messages:
            logger.debug("\nNo messages fit, returning most recent message")
            return [non_system_messages[-1].to_dict()]
        
        logger.debug(f"\n=== Final context ({len(included_messages)} messages, {total_tokens} tokens) ===")
        for i, msg in enumerate(included_messages):
            logger.debug(f"  {i}: {msg.role.upper()} - '{msg.content}' ({msg.token_count} tokens)")
            
        return [msg.to_dict() for msg in included_messages]
    
    def summarize(self, target_tokens: Optional[int] = None) -> str:
        """Generate a summary of the current conversation.
        
        Args:
            target_tokens: Target number of tokens for the summary.
                          If None, will use summary_ratio to determine.
                          
        Returns:
            String containing the summary
        """
        if not self.messages:
            return ""
        
        # If no target specified, calculate based on current token count and summary_ratio
        if target_tokens is None:
            target_tokens = int(self._current_tokens * self.summary_ratio)
        
        # Simple summarization strategy: take the most recent messages that fit
        summary_messages = []
        current_tokens = 0
        
        # Always include system messages
        system_messages = [msg for msg in self.messages if msg.role == 'system']
        sys_tokens = sum(msg.token_count for msg in system_messages)
        
        if sys_tokens > target_tokens:
            # If system messages alone exceed the target, we need to truncate them
            # This is not ideal but better than failing
            summary_messages = system_messages[:1]  # Just take the first system message
            current_tokens = summary_messages[0].token_count
        else:
            summary_messages = system_messages
            current_tokens = sys_tokens
        
        # Add recent messages until we hit the target
        remaining_messages = [msg for msg in self.messages if msg.role != 'system']
        
        for msg in reversed(remaining_messages):
            if current_tokens + msg.token_count > target_tokens:
                break
            summary_messages.append(msg)
            current_tokens += msg.token_count
        
        # Generate a summary string
        summary_parts = []
        for msg in summary_messages:
            prefix = f"{msg.role.upper()}:"
            if msg.name:
                prefix = f"{prefix} {msg.name}:"
            summary_parts.append(f"{prefix} {msg.content}")
        
        # Add a note about truncated messages if any
        if len(summary_messages) < len(self.messages):
            summary_parts.append("... conversation truncated ...")
        
        summary = "\n".join(summary_parts)
        
        # Store the summary in our buffer
        self._summary_buffer.append(summary)
        self.total_summaries_created += 1
        
        # Calculate tokens saved
        original_tokens = self._current_tokens
        self._current_tokens = self.tokenizer.count_tokens(summary)
        tokens_saved = original_tokens - self._current_tokens
        self.total_tokens_saved += max(0, tokens_saved)
        
        # Update messages to just contain the summary
        self.messages = [Message(role="system", content=summary)]
        self._message_hashes = {self._hash_message(self.messages[0])}
        
        return summary
    
    def clear(self) -> None:
        """Clear the current context."""
        self.messages.clear()
        self._current_tokens = 0
        self._message_hashes.clear()
        self._summary_buffer.clear()
    
    def save_session(self, session_id: Optional[str] = None) -> str:
        """Save the current conversation state to disk.
        
        Args:
            session_id: Optional session ID. If None, will generate one.
            
        Returns:
            The session ID used to save the state
        """
        if not session_id:
            if not self._conversation_id:
                self._conversation_id = self._generate_session_id()
            session_id = self._conversation_id
        
        session_data = {
            'version': '1.0',
            'session_id': session_id,
            'messages': [msg.__dict__ for msg in self.messages],
            'summary_buffer': self._summary_buffer,
            'statistics': {
                'total_tokens_processed': self.total_tokens_processed,
                'total_messages_processed': self.total_messages_processed,
                'total_summaries_created': self.total_summaries_created,
                'total_tokens_saved': self.total_tokens_saved,
            },
            'timestamp': time.time(),
        }
        
        session_file = self.persistence_dir / f"{session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        return session_id
    
    def load_session(self, session_id: str) -> bool:
        """Load a conversation state from disk.
        
        Args:
            session_id: The session ID to load
            
        Returns:
            True if the session was loaded successfully, False otherwise
        """
        session_file = self.persistence_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return False
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Clear current state
            self.clear()
            
            # Load messages
            self.messages = [Message.from_dict(msg) for msg in session_data.get('messages', [])]
            self._summary_buffer = session_data.get('summary_buffer', [])
            self._conversation_id = session_data.get('session_id')
            
            # Recalculate token counts
            self._current_tokens = sum(msg.token_count for msg in self.messages)
            self._message_hashes = {self._hash_message(msg) for msg in self.messages}
            
            # Update statistics
            stats = session_data.get('statistics', {})
            self.total_tokens_processed = stats.get('total_tokens_processed', 0)
            self.total_messages_processed = stats.get('total_messages_processed', 0)
            self.total_summaries_created = stats.get('total_summaries_created', 0)
            self.total_tokens_saved = stats.get('total_tokens_saved', 0)
            
            return True
            
        except (json.JSONDecodeError, KeyError, OSError) as e:
            # Log the error and return False
            return False
    
    def list_sessions(self) -> List[Dict]:
        """List all available saved sessions.
        
        Returns:
            List of dictionaries with session information
        """
        sessions = []
        
        for session_file in self.persistence_dir.glob("*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                sessions.append({
                    'session_id': session_data.get('session_id', session_file.stem),
                    'timestamp': session_data.get('timestamp'),
                    'message_count': len(session_data.get('messages', [])),
                    'summary_count': len(session_data.get('summary_buffer', [])),
                    'file': str(session_file)
                })
            except (json.JSONDecodeError, OSError):
                continue
        
        # Sort by timestamp, newest first
        sessions.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        return sessions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the context manager's usage."""
        return {
            'current_messages': len(self.messages),
            'current_tokens': self._current_tokens,
            'max_tokens': self.max_tokens,
            'token_usage_pct': (self._current_tokens / self.max_tokens * 100) if self.max_tokens > 0 else 0,
            'total_messages_processed': self.total_messages_processed,
            'total_tokens_processed': self.total_tokens_processed,
            'total_summaries_created': self.total_summaries_created,
            'total_tokens_saved': self.total_tokens_saved,
            'summaries_in_buffer': len(self._summary_buffer)
        }
    
    def _enforce_limits(self) -> None:
        """Ensure we're not exceeding token or message limits."""
        # Check if we need to summarize
        if self._current_tokens > self.max_tokens * self.summary_threshold:
            self.summarize()
        
        # If still over the limit after summarizing, trim oldest messages
        while self._current_tokens > self.max_tokens and len(self.messages) > 1:
            removed = self.messages.pop(0)
            self._current_tokens -= removed.token_count
            self._message_hashes.discard(self._hash_message(removed))
        
        # Enforce max messages
        while len(self.messages) > self.max_messages:
            removed = self.messages.pop(0)
            self._current_tokens -= removed.token_count
            self._message_hashes.discard(self._hash_message(removed))
    
    def _count_message_tokens(self, message: Message) -> int:
        """Count tokens in a message."""
        # Count base message tokens
        count = 4  # Start with 4 tokens for the message structure
        
        # Count content tokens
        if message.content:
            count += self.tokenizer.count_tokens(message.content)
        
        # Count function call tokens if present
        if message.function_call:
            # Add tokens for function call structure
            count += 10  # Approximate for the structure
            
            # Add tokens for function name and arguments
            if 'name' in message.function_call:
                count += self.tokenizer.count_tokens(message.function_call['name'])
            if 'arguments' in message.function_call:
                count += self.tokenizer.count_tokens(message.function_call['arguments'])
        
        # Add tokens for role and name if present
        count += self.tokenizer.count_tokens(message.role)
        if message.name:
            count += self.tokenizer.count_tokens(message.name)
        
        return count
    
    @staticmethod
    def _hash_message(message: Message) -> str:
        """Generate a hash for a message to detect duplicates."""
        content = f"{message.role}:{message.name or ''}:{message.content}"
        if message.function_call:
            content += f":{message.function_call.get('name', '')}:{message.function_call.get('arguments', '')}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def _generate_session_id() -> str:
        """Generate a unique session ID."""
        return f"sess_{int(time.time())}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
