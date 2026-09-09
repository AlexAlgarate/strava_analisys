from collections.abc import Mapping
from dataclasses import dataclass
from typing import Self


@dataclass(frozen=True, slots=True)
class TokenSet:
    """OAuth tokens returned by Strava."""

    access_token: str
    refresh_token: str
    expires_at: int

    def __post_init__(self) -> None:
        if not self.access_token:
            raise ValueError("Access token cannot be empty.")
        if not self.refresh_token:
            raise ValueError("Refresh token cannot be empty.")
        if self.expires_at <= 0:
            raise ValueError("Token expiration must be a positive Unix timestamp.")

    @classmethod
    def from_mapping(cls, payload: Mapping[str, object]) -> Self:
        access_token = payload.get("access_token")
        refresh_token = payload.get("refresh_token")
        expires_at = payload.get("expires_at")

        if not isinstance(access_token, str):
            raise TypeError("Token payload must contain a string access_token.")
        if not isinstance(refresh_token, str):
            raise TypeError("Token payload must contain a string refresh_token.")
        if isinstance(expires_at, bool) or not isinstance(expires_at, int):
            raise TypeError("Token payload must contain an integer expires_at.")

        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )

    def is_expired(self, now: int) -> bool:
        return self.expires_at <= now

    def as_dict(self) -> dict[str, str | int]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_at": self.expires_at,
        }
