#!/usr/bin/env bash
# Twitch Plays Bot Startup Script

# Set SSL certificates
export SSL_CERT_FILE=$(uv run python -c "import certifi; print(certifi.where())")

# Run the bot
echo "Starting Twitch Plays Bot..."
uv run python -m twitch_plays.main
