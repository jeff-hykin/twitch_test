"""Configuration management for Twitch Plays bot."""
from pydantic import Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TwitchConfig(BaseSettings):
    """Configuration for Twitch Plays bot loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env file
    )

    # Twitch Authentication
    twitch_token: str = Field(..., description="OAuth token for Twitch (must start with 'oauth:')")
    channel_name: str = Field(..., description="Twitch channel name to join")

    # Bot Configuration
    bot_prefix: str = Field(default="!", description="Command prefix for bot commands")
    commands_str: str = Field(
        default="forward,back,left,right",
        description="Comma-separated list of valid commands",
        alias="COMMANDS",
    )

    @computed_field
    @property
    def commands(self) -> list[str]:
        """Parse commands from comma-separated string."""
        return [cmd.strip().lower() for cmd in self.commands_str.split(",") if cmd.strip()]

    # Voting Configuration
    vote_window_seconds: float = Field(
        default=10.0, description="Duration of voting window in seconds", gt=0
    )
    min_votes_threshold: int = Field(
        default=1, description="Minimum votes required to trigger action", ge=1
    )

    @field_validator("twitch_token")
    @classmethod
    def validate_oauth_token(cls, v: str) -> str:
        """Ensure OAuth token has correct format."""
        if not v.startswith("oauth:"):
            raise ValueError("Twitch token must start with 'oauth:'")
        return v

    @field_validator("commands_str")
    @classmethod
    def validate_commands_str(cls, v: str) -> str:
        """Ensure commands string is not empty."""
        if not v or not v.strip():
            raise ValueError("Commands cannot be empty")
        return v
