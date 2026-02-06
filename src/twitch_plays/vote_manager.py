"""Vote management system for Twitch Plays bot."""
import asyncio
import time
from collections import Counter, deque
from collections.abc import Callable, Awaitable
from typing import Optional


class VoteManager:
    """Manages vote collection and aggregation over time windows."""

    def __init__(
        self,
        commands: list[str],
        window_seconds: float,
        min_votes_threshold: int,
        action_handler: Callable[[str], Awaitable[None]],
    ):
        """
        Initialize the vote manager.

        Args:
            commands: List of valid commands
            window_seconds: Duration of voting window in seconds
            min_votes_threshold: Minimum votes required to trigger action
            action_handler: Async function to call with winning command
        """
        self.commands = set(commands)
        self.window_seconds = window_seconds
        self.min_votes_threshold = min_votes_threshold
        self.action_handler = action_handler

        # Store votes as (command, timestamp) tuples
        self._votes: deque[tuple[str, float]] = deque()
        self._voting_task: Optional[asyncio.Task] = None
        self._running = False

    def record_vote(self, command: str) -> None:
        """
        Record a vote for a command.

        Args:
            command: The command that was voted for
        """
        if command not in self.commands:
            return

        timestamp = time.time()
        self._votes.append((command, timestamp))

    def get_winning_command(self) -> Optional[str]:
        """
        Get the most popular command from current votes.

        Returns:
            The winning command, or None if below threshold
        """
        self._clear_old_votes()

        if not self._votes:
            return None

        # Count votes for each command
        vote_counts = Counter(cmd for cmd, _ in self._votes)

        # Check if we meet minimum threshold
        total_votes = sum(vote_counts.values())
        if total_votes < self.min_votes_threshold:
            return None

        # Return command with most votes (first in case of tie)
        winning_command, _ = vote_counts.most_common(1)[0]
        return winning_command

    def _clear_old_votes(self) -> None:
        """Remove votes older than the voting window."""
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds

        # Remove votes from the left (oldest) until we hit recent votes
        while self._votes and self._votes[0][1] < cutoff_time:
            self._votes.popleft()

    async def _voting_loop(self) -> None:
        """Main voting loop that periodically tallies votes and triggers actions."""
        while self._running:
            await asyncio.sleep(self.window_seconds)

            # Clear old votes and get winner
            winning_command = self.get_winning_command()

            if winning_command:
                await self.action_handler(winning_command)

            # Clear votes after processing
            self._votes.clear()

    def start_voting_loop(self) -> asyncio.Task:
        """
        Start the voting loop as a background task.

        Returns:
            The asyncio Task running the voting loop
        """
        if self._voting_task and not self._voting_task.done():
            raise RuntimeError("Voting loop is already running")

        self._running = True
        self._voting_task = asyncio.create_task(self._voting_loop())
        return self._voting_task

    async def stop_voting_loop(self) -> None:
        """Stop the voting loop."""
        self._running = False
        if self._voting_task:
            self._voting_task.cancel()
            try:
                await self._voting_task
            except asyncio.CancelledError:
                pass
