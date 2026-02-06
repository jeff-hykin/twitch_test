"""Tests for the VoteManager class."""
import asyncio
import time
from unittest.mock import AsyncMock

import pytest

from src.twitch_plays.vote_manager import VoteManager


@pytest.fixture
def mock_action_handler():
    """Create a mock action handler."""
    return AsyncMock()


@pytest.fixture
def vote_manager(mock_action_handler):
    """Create a VoteManager instance for testing."""
    return VoteManager(
        commands=["forward", "back", "left", "right"],
        window_seconds=1.0,  # Short window for fast tests
        min_votes_threshold=1,
        action_handler=mock_action_handler,
    )


def test_record_vote_valid_command(vote_manager):
    """Test recording a valid vote."""
    vote_manager.record_vote("forward")
    assert len(vote_manager._votes) == 1
    assert vote_manager._votes[0][0] == "forward"


def test_record_vote_invalid_command(vote_manager):
    """Test that invalid commands are ignored."""
    vote_manager.record_vote("invalid")
    assert len(vote_manager._votes) == 0


def test_record_multiple_votes(vote_manager):
    """Test recording multiple votes."""
    vote_manager.record_vote("forward")
    vote_manager.record_vote("back")
    vote_manager.record_vote("forward")
    assert len(vote_manager._votes) == 3


def test_get_winning_command_single_vote(vote_manager):
    """Test getting winner with a single vote."""
    vote_manager.record_vote("forward")
    winner = vote_manager.get_winning_command()
    assert winner == "forward"


def test_get_winning_command_multiple_votes(vote_manager):
    """Test getting winner with multiple votes."""
    vote_manager.record_vote("forward")
    vote_manager.record_vote("forward")
    vote_manager.record_vote("back")
    vote_manager.record_vote("forward")

    winner = vote_manager.get_winning_command()
    assert winner == "forward"


def test_get_winning_command_tie(vote_manager):
    """Test that ties are broken by first occurrence."""
    vote_manager.record_vote("forward")
    vote_manager.record_vote("back")

    winner = vote_manager.get_winning_command()
    # Should return one of them (Counter.most_common is deterministic for equal counts)
    assert winner in ["forward", "back"]


def test_get_winning_command_no_votes(vote_manager):
    """Test getting winner with no votes."""
    winner = vote_manager.get_winning_command()
    assert winner is None


def test_get_winning_command_below_threshold(vote_manager, mock_action_handler):
    """Test that commands below threshold return None."""
    vm = VoteManager(
        commands=["forward", "back"],
        window_seconds=1.0,
        min_votes_threshold=3,
        action_handler=mock_action_handler,
    )

    vm.record_vote("forward")
    vm.record_vote("forward")

    winner = vm.get_winning_command()
    assert winner is None  # Only 2 votes, threshold is 3


def test_clear_old_votes(vote_manager):
    """Test that old votes are cleared."""
    # Record a vote
    vote_manager.record_vote("forward")
    assert len(vote_manager._votes) == 1

    # Wait for votes to become old (window is 1 second)
    time.sleep(1.1)

    # Clear old votes
    vote_manager._clear_old_votes()

    # Votes should be cleared
    assert len(vote_manager._votes) == 0


def test_clear_old_votes_keeps_recent(vote_manager):
    """Test that recent votes are kept."""
    vote_manager.record_vote("forward")
    time.sleep(0.5)  # Wait half the window
    vote_manager.record_vote("back")

    # Clear old votes
    vote_manager._clear_old_votes()

    # Both votes should still be there (window is 1 second)
    assert len(vote_manager._votes) == 2


@pytest.mark.asyncio
async def test_voting_loop_triggers_action(vote_manager, mock_action_handler):
    """Test that the voting loop triggers actions."""
    # Start voting loop first
    task = vote_manager.start_voting_loop()

    # Wait a bit, then record some votes during the voting window
    await asyncio.sleep(0.1)
    vote_manager.record_vote("forward")
    vote_manager.record_vote("forward")
    vote_manager.record_vote("back")

    # Wait for the voting cycle to complete (1 second window + buffer for processing)
    await asyncio.sleep(1.5)

    # Stop the loop
    await vote_manager.stop_voting_loop()

    # Action handler should have been called with "forward"
    mock_action_handler.assert_called_once_with("forward")


@pytest.mark.asyncio
async def test_voting_loop_no_action_below_threshold(vote_manager, mock_action_handler):
    """Test that voting loop doesn't trigger action below threshold."""
    # Create manager with higher threshold
    vm = VoteManager(
        commands=["forward", "back"],
        window_seconds=1.0,
        min_votes_threshold=5,
        action_handler=mock_action_handler,
    )

    # Record only 2 votes (below threshold of 5)
    vm.record_vote("forward")
    vm.record_vote("forward")

    # Start voting loop
    task = vm.start_voting_loop()

    # Wait for one voting cycle
    await asyncio.sleep(1.5)

    # Stop the loop
    await vm.stop_voting_loop()

    # Action handler should NOT have been called
    mock_action_handler.assert_not_called()


@pytest.mark.asyncio
async def test_start_voting_loop_raises_if_already_running(vote_manager):
    """Test that starting the loop twice raises an error."""
    task = vote_manager.start_voting_loop()

    with pytest.raises(RuntimeError, match="already running"):
        vote_manager.start_voting_loop()

    await vote_manager.stop_voting_loop()


@pytest.mark.asyncio
async def test_stop_voting_loop(vote_manager):
    """Test stopping the voting loop."""
    task = vote_manager.start_voting_loop()
    assert not task.done()

    await vote_manager.stop_voting_loop()
    assert task.done()


@pytest.mark.asyncio
async def test_votes_cleared_after_processing(vote_manager, mock_action_handler):
    """Test that votes are cleared after each voting cycle."""
    # Record votes
    vote_manager.record_vote("forward")
    vote_manager.record_vote("forward")

    # Start voting loop
    task = vote_manager.start_voting_loop()

    # Wait for one voting cycle
    await asyncio.sleep(1.5)

    # Votes should be cleared
    assert len(vote_manager._votes) == 0

    await vote_manager.stop_voting_loop()
