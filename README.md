# Twitch Plays X

A "Twitch Plays" style server that listens to a Twitch stream's chat, collects command votes from viewers, and periodically executes the most popular command.

## Features

- **Real-time vote collection** from Twitch chat
- **Time-based voting windows** (configurable, default 10 seconds)
- **Automatic command aggregation** - most popular command wins
- **Async architecture** using Python's asyncio and TwitchIO
- **Easy configuration** via environment variables
- **Extensible action system** - replace PLACEHOLDER_ACTION with your game controls

## Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) - Modern Python package manager
- Twitch account for the bot
- Twitch OAuth token and Client ID

## Installation

1. **Clone the repository** (or navigate to your project directory):
   ```bash
   cd twitch_test
   ```

2. **Install dependencies** using uv:
   ```bash
   uv sync
   ```

## Configuration

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Get your Twitch credentials**:
   - Go to [Twitch Token Generator](https://twitchtokengenerator.com/)
   - Select "Bot Chat Token"
   - Authorize with your bot account
   - Copy the OAuth token (it should start with `oauth:`)
   - Copy the Client ID

   Alternatively, create an application at the [Twitch Developer Console](https://dev.twitch.tv/console/apps).

3. **Edit `.env` file** with your credentials:
   ```bash
   TWITCH_TOKEN=oauth:your_actual_token_here
   TWITCH_CLIENT_ID=your_actual_client_id_here
   CHANNEL_NAME=your_channel_name
   ```

4. **Optional: Customize settings** in `.env`:
   - `BOT_PREFIX` - Command prefix (default: `!`)
   - `COMMANDS` - Comma-separated list of commands (default: `forward,back,left,right`)
   - `VOTE_WINDOW_SECONDS` - Voting window duration (default: `10.0`)
   - `MIN_VOTES_THRESHOLD` - Minimum votes to trigger action (default: `1`)

## Usage

### Running the Bot

Start the bot with uv:
```bash
uv run python -m twitch_plays.main
```

Or using the src path:
```bash
uv run python -m src.twitch_plays.main
```

### How It Works

1. The bot connects to your specified Twitch channel
2. Viewers send commands in chat using the prefix (e.g., `!forward`, `!back`)
3. Votes are collected over the configured time window (default: 10 seconds)
4. After each window, the most popular command is executed
5. The action is logged to console (currently calls `PLACEHOLDER_ACTION`)

### Example

If viewers send these commands in 10 seconds:
- User1: `!forward`
- User2: `!forward`
- User3: `!left`
- User4: `!forward`

The bot will execute: `forward` (3 votes vs 1 vote)

## Development

### Running Tests

```bash
uv run pytest
```

### Project Structure

```
twitch_test/
├── src/
│   └── twitch_plays/
│       ├── __init__.py         # Package initialization
│       ├── main.py             # Entry point
│       ├── bot.py              # TwitchIO bot implementation
│       ├── vote_manager.py     # Voting system
│       ├── config.py           # Configuration management
│       └── actions.py          # Action handlers (PLACEHOLDER_ACTION)
├── tests/
│   └── test_vote_manager.py    # Unit tests
├── pyproject.toml              # Project dependencies
├── .env.example                # Configuration template
└── README.md                   # This file
```

## Extending the Bot

### Adding Game Controls

Replace the `PLACEHOLDER_ACTION` function in `src/twitch_plays/actions.py`:

```python
import pyautogui  # Example: keyboard simulation

async def PLACEHOLDER_ACTION(command: str) -> None:
    """Execute game command."""
    if command == "forward":
        pyautogui.press("w")
    elif command == "back":
        pyautogui.press("s")
    elif command == "left":
        pyautogui.press("a")
    elif command == "right":
        pyautogui.press("d")
```

### Adding More Commands

Edit your `.env` file:
```bash
COMMANDS=forward,back,left,right,jump,crouch,sprint
```

## Troubleshooting

### "Configuration error" on startup
- Check that your `.env` file exists and has all required fields
- Ensure `TWITCH_TOKEN` starts with `oauth:`
- Verify your Client ID is correct

### Bot doesn't respond to commands
- Check that the bot has joined the correct channel (see console output)
- Ensure commands use the correct prefix (default: `!`)
- Verify commands are in the `COMMANDS` list in `.env`
- Commands are case-insensitive: `!FORWARD` and `!forward` both work

### "Failed to connect" errors
- Check your internet connection
- Verify your OAuth token is valid (tokens can expire)
- Try regenerating your token at [Twitch Token Generator](https://twitchtokengenerator.com/)

## License

MIT

## Contributing

Contributions welcome! Please open an issue or pull request.
