from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class TokenSet:
    """OAuth tokens returned by Strava."""

    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    expires_at: int

    def __post_init__(self) -> None:
        if not isinstance(self.access_token, str):
            raise TypeError("Access token must be a string.")
        if not self.access_token.strip():
            raise ValueError("Access token cannot be blank.")
        if not isinstance(self.refresh_token, str):
            raise TypeError("Refresh token must be a string.")
        if not self.refresh_token.strip():
            raise ValueError("Refresh token cannot be blank.")
        if isinstance(self.expires_at, bool) or not isinstance(self.expires_at, int):
            raise TypeError("Token expiration must be an integer Unix timestamp.")
        if self.expires_at <= 0:
            raise ValueError("Token expiration must be a positive Unix timestamp.")

    def is_expired(self, now: int) -> bool:
        return self.expires_at <= now
