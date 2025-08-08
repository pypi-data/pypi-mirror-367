import asyncio
import sys

from . import server


def cli_main():
    """Main entry point for the package."""
    # Handle platform-specific configurations
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    server.main()


# Expose main function for script entry
__all__ = ["cli_main", "server"]
