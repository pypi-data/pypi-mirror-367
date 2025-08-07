"""Terminal utilities for the Qwen3-Coder CLI."""
import sys
import re
import shutil
from typing import Optional, List, Tuple, Callable, Any
from dataclasses import dataclass
from enum import Enum, auto

from prompt_toolkit import print_formatted_text, HTML
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.formatters import TerminalFormatter
from pygments.util import ClassNotFound

# ANSI color codes
class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class MessageType(Enum):
    """Types of messages for styling."""
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    SYSTEM = auto()
    USER = auto()
    ASSISTANT = auto()
    CODE = auto()
    PROMPT = auto()

@dataclass
class TerminalStyle:
    """Style configuration for terminal output."""
    width: int = 80
    show_help_hint: bool = True
    show_token_count: bool = True
    syntax_highlighting: bool = True
    color_scheme: str = "default"  # 'default', 'dark', 'light', 'monochrome'
    
    def __post_init__(self):
        self.update_width()
    
    def update_width(self):
        """Update terminal width from current console size."""
        try:
            self.width = min(shutil.get_terminal_size().columns - 2, 120)
        except:
            self.width = 80

class Terminal:
    """Handles all terminal output with styling and formatting."""
    
    def __init__(self, style: Optional[TerminalStyle] = None):
        self.style = style or TerminalStyle()
        self._init_styles()
    
    def _init_styles(self):
        """Initialize the style dictionary based on color scheme."""
        if self.style.color_scheme == "dark":
            self.styles = {
                MessageType.INFO: "#87CEEB",  # SkyBlue
                MessageType.SUCCESS: "#90EE90",  # LightGreen
                MessageType.WARNING: "#FFD700",  # Yellow
                MessageType.ERROR: "#FF6B6B",  # LightRed
                MessageType.SYSTEM: "#98FB98",  # PaleGreen
                MessageType.USER: "#87CEEB",  # SkyBlue
                MessageType.ASSISTANT: "#FFFFFF",  # White
                MessageType.CODE: "#F5F5F5",  # WhiteSmoke
                MessageType.PROMPT: "#FFA500",  # Orange
            }
        elif self.style.color_scheme == "light":
            self.styles = {
                MessageType.INFO: "#0000FF",  # Blue
                MessageType.SUCCESS: "#006400",  # DarkGreen
                MessageType.WARNING: "#8B4513",  # SaddleBrown
                MessageType.ERROR: "#8B0000",  # DarkRed
                MessageType.SYSTEM: "#2E8B57",  # SeaGreen
                MessageType.USER: "#000080",  # Navy
                MessageType.ASSISTANT: "#000000",  # Black
                MessageType.CODE: "#2F4F4F",  # DarkSlateGray
                MessageType.PROMPT: "#8B008B",  # DarkMagenta
            }
        elif self.style.color_scheme == "monochrome":
            # Use different weights and styles for monochrome
            self.styles = {
                MessageType.INFO: "",
                MessageType.SUCCESS: "bold",
                MessageType.WARNING: "italic",
                MessageType.ERROR: "bold italic",
                MessageType.SYSTEM: "",
                MessageType.USER: "",
                MessageType.ASSISTANT: "",
                MessageType.CODE: "",
                MessageType.PROMPT: "",
            }
        else:  # default
            self.styles = {
                MessageType.INFO: "ansicyan",
                MessageType.SUCCESS: "ansigreen",
                MessageType.WARNING: "ansiyellow",
                MessageType.ERROR: "ansired",
                MessageType.SYSTEM: "ansigreen",
                MessageType.USER: "ansicyan",
                MessageType.ASSISTANT: "ansibrightwhite",
                MessageType.CODE: "ansibrightwhite",
                MessageType.PROMPT: "ansiyellow",
            }
    
    def print(self, text: str, msg_type: MessageType = MessageType.INFO, end: str = "\n"):
        """Print formatted text to the terminal."""
        style = self.styles.get(msg_type, "")
        
        if self.style.color_scheme == "monochrome":
            formatted_text = f"{style}{text}{' ' if style else ''}{end}"
            print(formatted_text, end="")
        else:
            if style:
                text = f"<{style}>{text}</{style}>"
            print_formatted_text(HTML(text), end=end, style=Style.from_dict({
                '': 'default',
                'ansired': '#ff6b6b',
                'ansigreen': '#5fff87',
                'ansiyellow': '#f3ef7d',
                'ansiblue': '#57c7ff',
                'ansifuchsia': '#ff6ac1',
                'ansiturquoise': '#9aedfe',
                'ansilightgray': 'ansibrightblack',
                'ansidarkgray': 'ansibrightblack',
                'ansibrightred': '#ff5c57',
                'ansibrightgreen': '#5af78e',
                'ansibrightyellow': '#f4f99d',
                'ansibrightblue': '#57c7ff',
                'ansibrightmagenta': '#ff6ac1',
                'ansibrightcyan': '#9aedfe',
                'ansibrightwhite': '#f1f1f0',
            }))
    
    def print_header(self, text: str):
        """Print a section header."""
        self.print("\n" + "=" * self.style.width, MessageType.INFO)
        self.print(text.center(self.style.width), MessageType.INFO)
        self.print("=" * self.style.width + "\n", MessageType.INFO)
    
    def print_success(self, text: str):
        """Print a success message."""
        self.print(f"✓ {text}", MessageType.SUCCESS)
    
    def print_warning(self, text: str):
        """Print a warning message."""
        self.print(f"⚠ {text}", MessageType.WARNING)
    
    def print_error(self, text: str):
        """Print an error message."""
        self.print(f"✗ {text}", MessageType.ERROR)
    
    def print_system(self, text: str):
        """Print a system message."""
        self.print(f"\n[system] {text}", MessageType.SYSTEM)
    
    def print_user_message(self, text: str):
        """Print a user message."""
        self.print("\nYou:", MessageType.USER, end=" ")
        self.print(text, MessageType.USER)
    
    def print_assistant_message(self, text: str):
        """Print an assistant message with syntax highlighting."""
        self.print("\nAssistant:", MessageType.ASSISTANT, end=" ")
        
        # Split code blocks from regular text
        parts = self._split_code_blocks(text)
        
        for is_code, content in parts:
            if is_code:
                self._print_code_block(content)
            else:
                self.print(content, MessageType.ASSISTANT, end="")
        
        print()  # Final newline
    
    def _split_code_blocks(self, text: str) -> List[Tuple[bool, str]]:
        """Split text into code and non-code parts."""
        parts = []
        current_pos = 0
        
        # Find all code blocks (```lang ... ```)
        for match in re.finditer(r'```(\w*)\n(.*?)\n```', text, re.DOTALL):
            # Text before the code block
            if match.start() > current_pos:
                parts.append((False, text[current_pos:match.start()]))
            
            # The code block
            lang = match.group(1) or 'text'
            code = match.group(2)
            parts.append((True, (lang, code)))
            
            current_pos = match.end()
        
        # Remaining text after the last code block
        if current_pos < len(text):
            parts.append((False, text[current_pos:]))
        
        return parts
    
    def _print_code_block(self, code_info: Tuple[str, str]):
        """Print a code block with syntax highlighting."""
        lang, code = code_info
        
        if not self.style.syntax_highlighting:
            self.print(f"\n```{lang}\n{code}\n```\n", MessageType.CODE, end="")
            return
        
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            try:
                lexer = guess_lexer(code)
            except ClassNotFound:
                lexer = TextLexer()
        
        formatter = TerminalFormatter(style=self.style.color_scheme)
        
        # Print with syntax highlighting
        print()  # Newline before code block
        highlight(code, lexer, formatter, sys.stdout)
        print("\n", end="")  # Newline after code block
    
    def print_help(self, commands: List[Tuple[str, str]]):
        """Print a formatted help message."""
        self.print_header("Qwen3-Coder Terminal Agent - Help")
        
        # Calculate column widths
        cmd_width = max(len(cmd[0]) for cmd in commands) + 2
        desc_width = self.style.width - cmd_width - 4
        
        for cmd, desc in commands:
            # Split description into multiple lines if needed
            desc_lines = [desc[i:i+desc_width] for i in range(0, len(desc), desc_width)]
            
            # Print command and first line of description
            self.print(f"  {cmd.ljust(cmd_width)}", MessageType.PROMPT, end="")
            self.print(desc_lines[0] if desc_lines else "", MessageType.INFO)
            
            # Print additional description lines indented
            for line in desc_lines[1:]:
                self.print(" " * (cmd_width + 2) + line, MessageType.INFO)
        
        print()  # Final newline
    
    def print_token_usage(self, current: int, max_tokens: int, message_count: int):
        """Print a visual token usage meter."""
        if not self.style.show_token_count:
            return
        
        # Calculate percentages
        percentage = min(100, int((current / max_tokens) * 100))
        filled_width = int((self.style.width - 10) * (percentage / 100))
        
        # Create the meter
        meter = "[" + "=" * filled_width + " " * (self.style.width - 10 - filled_width) + "]"
        
        # Build the output string
        output = [
            "\nToken Usage:",
            f"\n{meter} {percentage}%",
            f"\n{current:,} / {max_tokens:,} tokens  •  {message_count} messages\n"
        ]
        
        # Print the output
        output_str = "\n".join(output)
        print(output_str, end="", flush=True)
    
    def get_input(self, prompt: str = "", default: str = "") -> str:
        """Get user input with a prompt."""
        try:
            if default:
                prompt = f"{prompt} [{default}]: "
            else:
                prompt = f"{prompt}: "
            
            # Use input() for basic compatibility
            if self.style.color_scheme != "monochrome":
                prompt = f"\033[93m{prompt}\033[0m"  # Yellow prompt
            
            result = input(prompt)
            return result.strip() or default
        except (EOFError, KeyboardInterrupt):
            print()  # Newline after ^C
            return ""
    
    def clear_screen(self):
        """Clear the terminal screen."""
        print("\033[H\033[J", end="")  # ANSI escape code to clear screen
    
    def get_terminal_size(self) -> Tuple[int, int]:
        """Get the current terminal size."""
        try:
            return shutil.get_terminal_size()
        except:
            return (80, 24)  # Default size if detection fails
