"""Command-line interface for Qwen3-Coder Terminal Agent."""
import os
import sys
import cmd
import shlex
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

from .config import config
from .context_manager import ContextManager, Message
from .api_client import QwenAPIClient
from .token_manager import TokenManager
from .rate_limiter import RateLimiter
from .token_utils import QwenTokenizer

class QwenCoderCLI(cmd.Cmd):
    """Command-line interface for Qwen3-Coder Terminal Agent."""
    
    intro = (
        "Qwen3-Coder Terminal Agent (MVP)\n"
        "Type /help or ? to list commands.\n"
    )
    prompt = "qwen3> "
    doc_header = "Available commands (type /help <command> for more info):"
    
    def __init__(self):
        """Initialize the CLI with required components."""
        super().__init__()
        
        # Initialize components
        self.tokenizer = QwenTokenizer()
        self.token_manager = TokenManager()
        self.rate_limiter = RateLimiter()
        self.context = ContextManager(
            max_tokens=config.MAX_CONTEXT_TOKENS,
            tokenizer=self.tokenizer
        )
        self.api_client = QwenAPIClient(
            api_key=config.QWEN_API_KEY,
            base_url=config.QWEN_API_BASE,
            token_manager=self.token_manager,
            rate_limiter=self.rate_limiter
        )
        
        # Session state
        self.current_session: Optional[str] = None
        self.running = True
        
        # Command aliases
        self.aliases = {
            '?': 'help',
            'quit': 'exit',
            'q': 'exit',
            'h': 'help',
            'l': 'load',
            's': 'save',
            'ls': 'sessions',
            't': 'tokens'
        }
    
    def cmdloop(self, intro=None):
        """Wrapper around cmdloop to handle keyboard interrupts gracefully."""
        while self.running:
            try:
                super().cmdloop(intro="")
                self.running = False
            except KeyboardInterrupt:
                print("\nUse '/exit' to quit or type your message to continue.")
                continue
            except Exception as e:
                print(f"Error: {e}")
                continue
    
    def emptyline(self):
        """Do nothing on empty input."""
        pass
    
    def default(self, line):
        """Handle unknown commands or chat messages."""
        line = line.strip()
        
        # Handle empty input
        if not line:
            return
            
        # Handle command (with or without leading '/')
        is_command = line.startswith('/')
        cmd_parts = line[1:].split() if is_command else line.split()
        
        if cmd_parts:  # If we have a command
            cmd = cmd_parts[0].lower()
            
            # Handle command aliases
            if cmd in self.aliases:
                cmd = self.aliases[cmd]
                # Replace the command part with the resolved command
                cmd_parts[0] = cmd
                line = ' '.join(cmd_parts)
            
            if hasattr(self, f'do_{cmd}'):
                # Remove leading / if present
                cmd_line = line[1:] if is_command else line
                return self.onecmd(cmd_line)
            elif is_command:  # Only show error for unknown commands with leading '/'
                print(f"Unknown command: {cmd}. Type /help for available commands.")
                return
        
        # If we get here, treat as a chat message
        self._handle_chat_message(line)
    
    def _handle_chat_message(self, message: str) -> None:
        """Process and send a chat message to the API."""
        if not message.strip():
            return
            
        try:
            # Add user message to context
            user_msg = Message(role="user", content=message)
            self.context.add_message(user_msg)
            
            # Get context for API
            messages = self.context.get_context()
            
            # Show typing indicator
            print("\nAssistant: ", end='', flush=True)
            
            # Stream the response
            full_response = ""
            for chunk in self.api_client.stream_chat_completion(messages):
                print(chunk, end='', flush=True)
                full_response += chunk
            print("\n")
            
            # Add assistant's response to context
            if full_response.strip():
                assistant_msg = Message(role="assistant", content=full_response)
                self.context.add_message(assistant_msg)
            
        except Exception as e:
            print(f"\nError: {e}")
    
    # ===== Command Handlers =====
    
    def do_help(self, arg):
        """Show help information.
        
        Usage: /help [command]
        """
        if arg:
            # Show help for specific command
            cmd = arg.lower()
            if cmd in self.aliases:
                cmd = self.aliases[cmd]
                
            if hasattr(self, f'do_{cmd}'):
                doc = getattr(self, f'do_{cmd}').__doc__
                if doc:
                    print(doc.strip())
                else:
                    print(f"No help available for '{cmd}'")
            else:
                print(f"Unknown command: {cmd}")
        else:
            # Show general help
            print("\nQwen3-Coder Terminal Agent (MVP)")
            print("=" * 40)
            print("\nAvailable commands (prefix with /):")
            
            # Get all command methods and their aliases
            commands = {}
            for name in self.get_names():
                if name.startswith('do_') and name != 'do_help':
                    cmd_name = name[3:]
                    # Find aliases for this command
                    aliases = [a for a, c in self.aliases.items() if c == cmd_name]
                    commands[cmd_name] = aliases
            
            # Sort commands alphabetically
            for cmd_name in sorted(commands.keys()):
                aliases = commands[cmd_name]
                alias_text = f" (aliases: {', '.join(aliases)})" if aliases else ""
                print(f"  {cmd_name}{alias_text}")
            
            print("\nType /help <command> for more information on a specific command.")
    
    def do_exit(self, arg):
        """Exit the application.
        
        Usage: /exit
               /quit
               /q
        """
        print("\nGoodbye!")
        self.running = False
        return True
    
    def do_clear(self, arg):
        """Clear the current conversation.
        
        Usage: /clear
        """
        self.context.clear()
        print("Conversation cleared.")
    
    def do_save(self, arg):
        """Save the current conversation to a session.
        
        Usage: /save [session_name]
        """
        session_name = arg.strip() or f"session_{int(time.time())}"
        try:
            session_id = self.context.save_session(session_name)
            self.current_session = session_id
            print(f"Session saved as: {session_name}")
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def do_load(self, arg):
        """Load a saved conversation session.
        
        Usage: /load <session_id>
               /l <session_id>
        """
        if not arg:
            print("Please specify a session ID to load. Use /sessions to list available sessions.")
            return
            
        try:
            if self.context.load_session(arg):
                self.current_session = arg
                print(f"Loaded session: {arg}")
            else:
                print(f"Session not found: {arg}")
        except Exception as e:
            print(f"Error loading session: {e}")
    
    def do_sessions(self, arg):
        """List all saved sessions.
        
        Usage: /sessions
               /ls
        """
        sessions = self.context.list_sessions()
        
        if not sessions:
            print("No saved sessions found.")
            return
        
        print("\nSaved Sessions:")
        print("-" * 60)
        print(f"{'ID':<10} {'Name':<30} {'Last Modified':<20} Messages")
        print("-" * 60)
        
        for session in sessions:
            session_id = session.get('session_id', 'N/A')
            name = session.get('name', 'Unnamed')
            modified = time.strftime(
                '%Y-%m-%d %H:%M',
                time.localtime(session.get('timestamp', 0))
            )
            msg_count = session.get('message_count', 0)
            
            # Truncate long names
            if len(name) > 25:
                name = name[:22] + '...'
            
            print(f"{session_id[:8]:<10} {name:<30} {modified:<20} {msg_count}")
        
        print()
    
    def do_tokens(self, arg):
        """Show token usage statistics.
        
        Usage: /tokens
               /t
        """
        stats = self.context.get_statistics()
        
        print("\nToken Usage:")
        print("-" * 40)
        print(f"Current context: {stats['current_tokens']:,} tokens")
        print(f"Context limit:   {stats['max_tokens']:,} tokens")
        print(f"Usage:           {stats['token_usage_pct']:.1f}% of limit")
        print()
        print(f"Messages in context: {stats['current_messages']}")
        print(f"Total messages processed: {stats['total_messages_processed']:,}")
        print(f"Total tokens processed:   {stats['total_tokens_processed']:,}")
        print(f"Tokens saved by summarization: {stats['total_tokens_saved']:,}")
        print()

def main():
    """Main entry point for the Qwen3-Coder CLI."""
    # Check for API key
    if not config.QWEN_API_KEY:
        print("Error: QWEN_API_KEY environment variable not set.")
        print("Please set it before running the application.")
        sys.exit(1)
    
    # Create and run the CLI
    cli = QwenCoderCLI()
    cli.cmdloop()

if __name__ == "__main__":
    main()
