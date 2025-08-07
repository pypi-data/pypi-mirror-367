"""Configuration management for Qwen3-Coder Terminal Agent."""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration with environment variables."""
    
    # API Configuration
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_API_BASE: str = os.getenv("QWEN_API_BASE", "https://api.qwen.ai/v1")
    API_BASE_URL: str = os.getenv("API_BASE_URL", f"{QWEN_API_BASE}/chat/completions")
    
    # Rate Limiting
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    INITIAL_RETRY_DELAY: int = int(os.getenv("INITIAL_RETRY_DELAY", "1"))
    MAX_RETRY_DELAY: int = int(os.getenv("MAX_RETRY_DELAY", "10"))
    
    # Token Management
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4096"))
    MAX_CONTEXT_TOKENS: int = int(os.getenv("MAX_CONTEXT_TOKENS", "32000"))
    WARNING_THRESHOLD: float = float(os.getenv("WARNING_THRESHOLD", "0.8"))
    
    # Model Configuration
    MODEL_NAME: str = "qwen3-coder"
    
    @classmethod
    def validate(cls) -> None:
        """Validate that all required configuration is present."""
        if not cls.QWEN_API_KEY:
            raise ValueError(
                "QWEN_API_KEY environment variable not set. "
                "Please set it in your .env file or environment variables."
            )

# Create a singleton instance
config = Config()
