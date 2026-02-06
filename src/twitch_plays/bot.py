"""Twitch bot implementation for Twitch Plays."""
import logging
from twitchio.ext import commands

from .config import TwitchConfig
from .vote_manager import VoteManager

logger = logging.getLogger(__name__)


class TwitchPlaysBot(commands.Bot):
    """Twitch bot that listens for commands and records votes."""

    def __init__(self, config: TwitchConfig, vote_manager: VoteManager):
        """
        Initialize the Twitch bot.

        Args:
            config: Twitch configuration
            vote_manager: Vote manager instance
        """
        super().__init__(
            token=config.twitch_token,
            prefix=config.bot_prefix,
            initial_channels=[config.channel_name],
        )
        self.config = config
        self.vote_manager = vote_manager

    async def event_ready(self):
        """Called when the bot is ready and connected to Twitch."""
        logger.info(f"Logged in as {self.nick}")
        logger.info(f"Connected to channel: {self.config.channel_name}")
        print(f"✅ Bot ready: {self.nick}")
        print(f"📺 Listening on: #{self.config.channel_name}")
        print(f"🎮 Commands: {', '.join(f'{self.config.bot_prefix}{cmd}' for cmd in self.config.commands)}")
        print(f"⏱️  Vote window: {self.config.vote_window_seconds}s")
        print()

    async def event_message(self, message):
        """
        Called when a message is received in chat.

        Args:
            message: The message object from TwitchIO
        """
        # Ignore messages from the bot itself
        if message.echo:
            return

        content = message.content.strip()

        # Check if message starts with command prefix
        if not content.startswith(self.config.bot_prefix):
            return

        # Extract command (remove prefix and convert to lowercase)
        command = content[len(self.config.bot_prefix):].strip().lower()

        # Only record vote if it's a valid command
        if command in self.config.commands:
            self.vote_manager.record_vote(command)
            logger.debug(f"Vote recorded: {command} from {message.author.name}")
