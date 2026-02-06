"""Main entry point for Twitch Plays bot."""
import asyncio
import logging
import sys
from pathlib import Path

from pydantic import ValidationError

from .actions import PLACEHOLDER_ACTION
from .bot import TwitchPlaysBot
from .config import TwitchConfig
from .vote_manager import VoteManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


async def main():
    """Main application entry point."""
    print("🚀 Starting Twitch Plays Bot...")
    print()

    # Load configuration
    try:
        config = TwitchConfig()
        logger.info("Configuration loaded successfully")
    except ValidationError as e:
        logger.error("Configuration error:")
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            logger.error(f"  {field}: {error['msg']}")
        logger.error("\nPlease check your .env file or environment variables")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning("⚠️  No .env file found. Using environment variables.")
        logger.warning("   Copy .env.example to .env and configure your settings.")
        print()

    # Initialize vote manager
    vote_manager = VoteManager(
        commands=config.commands,
        window_seconds=config.vote_window_seconds,
        min_votes_threshold=config.min_votes_threshold,
        action_handler=PLACEHOLDER_ACTION,
    )

    # Start voting loop
    voting_task = vote_manager.start_voting_loop()
    logger.info("Voting loop started")

    # Initialize and run bot
    bot = TwitchPlaysBot(config=config, vote_manager=vote_manager)

    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Bot error: {e}", exc_info=True)
    finally:
        # Clean up
        await vote_manager.stop_voting_loop()
        voting_task.cancel()
        try:
            await voting_task
        except asyncio.CancelledError:
            pass
        logger.info("Cleanup complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
