"""Session management for Qwen3-Coder Terminal Agent."""
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from .config import config
from .token_manager import TokenManager
from .exceptions import SessionError, TokenLimitExceededError

class Session:
    """Manages conversation sessions with token awareness."""
    
    def __init__(self, session_id: Optional[str] = None, max_history: int = 20):
        """Initialize a new session.
        
        Args:
            session_id: Optional session ID. If None, a new ID will be generated.
            max_history: Maximum number of messages to keep in history.
        """
        self.session_id = session_id or f"session_{int(datetime.now().timestamp())}"
        self.messages: List[Dict[str, str]] = []
        self.metadata: Dict[str, Any] = {
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'model': config.MODEL_NAME,
        }
        self.max_history = max_history
        self.token_manager = TokenManager()
        
    def add_message(self, role: str, content: str, name: Optional[str] = None) -> None:
        """Add a message to the session.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
            name: Optional name for the message sender
            
        Raises:
            TokenLimitExceededError: If adding the message would exceed token limits
        """
        message = {"role": role, "content": content}
        if name:
            message["name"] = name
            
        # Check if adding this message would exceed token limits
        test_messages = self.messages + [message]
        within_limit, _, available = self.token_manager.check_context_limit(
            test_messages, config.MAX_TOKENS
        )
        
        if not within_limit:
            # Try to trim old messages first
            try:
                self.messages = self.token_manager.enforce_token_limit(
                    test_messages, config.MAX_TOKENS
                )
            except TokenLimitExceededError as e:
                raise TokenLimitExceededError(
                    f"Message too long. Please reduce the length of your input. {e}",
                    max_tokens=e.max_tokens,
                    requested_tokens=e.requested_tokens,
                )
        else:
            self.messages = test_messages
            
        # Update metadata
        self.metadata['updated_at'] = datetime.now().isoformat()
        self.metadata['message_count'] = len(self.messages)
        
        # Trim history if needed
        if len(self.messages) > self.max_history:
            # Keep system messages and recent messages
            system_messages = [m for m in self.messages if m.get("role") == "system"]
            other_messages = [m for m in self.messages if m.get("role") != "system"]
            self.messages = system_messages + other_messages[-(self.max_history - len(system_messages)):]
    
    def add_system_message(self, content: str) -> None:
        """Add a system message to the session."""
        self.add_message("system", content)
    
    def add_user_message(self, content: str, name: Optional[str] = None) -> None:
        """Add a user message to the session."""
        self.add_message("user", content, name)
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the session."""
        self.add_message("assistant", content)
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get all messages in the session."""
        return self.messages.copy()
    
    def clear(self) -> None:
        """Clear all messages except system messages."""
        system_messages = [m for m in self.messages if m.get("role") == "system"]
        self.messages = system_messages
        self.metadata['updated_at'] = datetime.now().isoformat()
        self.metadata['message_count'] = len(self.messages)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to a dictionary for serialization."""
        return {
            'session_id': self.session_id,
            'messages': self.messages,
            'metadata': self.metadata,
            'token_usage': self.token_manager.get_usage_stats(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create a session from a dictionary."""
        session = cls(session_id=data.get('session_id'))
        session.messages = data.get('messages', [])
        session.metadata = data.get('metadata', {})
        
        # Update token usage if available
        if 'token_usage' in data:
            session.token_manager.update_usage(data['token_usage'])
            
        return session
    
    def save(self, directory: str = ".sessions") -> str:
        """Save session to a file.
        
        Args:
            directory: Directory to save the session file in
            
        Returns:
            Path to the saved session file
        """
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f"{self.session_id}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            
        return filepath
    
    @classmethod
    def load(cls, session_id: str, directory: str = ".sessions") -> 'Session':
        """Load a session from a file.
        
        Args:
            session_id: ID of the session to load
            directory: Directory where session files are stored
            
        Returns:
            Loaded Session instance
            
        Raises:
            SessionError: If the session file doesn't exist or is invalid
        """
        filepath = os.path.join(directory, f"{session_id}.json")
        
        if not os.path.exists(filepath):
            raise SessionError(f"Session {session_id} not found in {directory}")
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return cls.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            raise SessionError(f"Invalid session file: {e}") from e
    
    def get_token_usage(self) -> Dict[str, int]:
        """Get current token usage statistics."""
        return self.token_manager.get_usage_stats()
    
    def get_available_tokens(self) -> int:
        """Get the number of tokens available in the context window."""
        _, _, available = self.token_manager.check_context_limit(
            self.messages, config.MAX_TOKENS
        )
        return available
