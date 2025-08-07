"""Main entry point for the Qwen3-Coder Terminal Agent."""

def main():
    """Run the Qwen3-Coder CLI."""
    from .cli import main as cli_main
    cli_main()

if __name__ == "__main__":
    main()
