import secrets
import webbrowser
from collections.abc import Callable
from dataclasses import dataclass
from urllib import parse

type BrowserOpener = Callable[[str], object]
type InputReader = Callable[[str], str]
type StateFactory = Callable[[], str]


def _generate_state() -> str:
    return secrets.token_urlsafe(32)


@dataclass(frozen=True, slots=True)
class StravaAuthorizationConfig:
    """Configuration required to start Strava's browser authorization flow."""

    client_id: str
    authorization_url: str = "https://www.strava.com/oauth/authorize"
    redirect_uri: str = "http://localhost/exchange_token"
    scope: str = "read,activity:read_all"

    def __post_init__(self) -> None:
        if not isinstance(self.client_id, str):
            raise TypeError("Strava client ID must be a string.")
        if not self.client_id.strip():
            raise ValueError("Strava client ID cannot be empty.")
        authorization = _absolute_url(
            self.authorization_url,
            label="Strava authorization URL",
        )
        if authorization.scheme != "https":
            raise ValueError("Strava authorization URL must use HTTPS.")
        redirect = _absolute_url(self.redirect_uri, label="Strava redirect URI")
        if redirect.scheme not in {"http", "https"}:
            raise ValueError("Strava redirect URI must use HTTP or HTTPS.")
        if redirect.scheme == "http" and redirect.hostname not in {
            "localhost",
            "127.0.0.1",
            "::1",
        }:
            raise ValueError("An HTTP Strava redirect must use a loopback host.")
        if not isinstance(self.scope, str):
            raise TypeError("Strava OAuth scope must be a string.")
        if not self.scope.strip():
            raise ValueError("Strava OAuth scope cannot be empty.")

    def as_query_params(self, *, state: str) -> dict[str, str]:
        if not isinstance(state, str):
            raise TypeError("OAuth state must be a string.")
        if not state.strip():
            raise ValueError("OAuth state cannot be empty.")
        return {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "approval_prompt": "force",
            "scope": self.scope,
            "state": state,
        }


class BrowserAuthorizationCodeProvider:
    """Obtain an OAuth code through the user's default browser."""

    def __init__(
        self,
        config: StravaAuthorizationConfig,
        *,
        opener: BrowserOpener | None = None,
        input_reader: InputReader | None = None,
        state_factory: StateFactory | None = None,
    ) -> None:
        self._config = config
        self._opener = opener if opener is not None else webbrowser.open
        self._input_reader = input_reader if input_reader is not None else input
        self._state_factory = (
            state_factory if state_factory is not None else _generate_state
        )

    def get_authorization_code(self) -> str:
        state = self._state_factory()
        auth_url = self._create_full_url(
            self._config.authorization_url,
            self._config.as_query_params(state=state),
        )
        self._opener(auth_url)
        callback_url = self._input_reader(
            "Paste here the URL from the browser: "
        ).strip()
        return self._extract_code(
            callback_url,
            expected_state=state,
            redirect_uri=self._config.redirect_uri,
        )

    @staticmethod
    def _create_full_url(base_url: str, params: dict[str, str]) -> str:
        url_parts = list(parse.urlparse(base_url))
        url_parts[4] = parse.urlencode(params)
        return parse.urlunparse(url_parts)

    @staticmethod
    def _extract_code(
        url: str,
        *,
        expected_state: str,
        redirect_uri: str,
    ) -> str:
        callback = parse.urlsplit(url)
        expected_redirect = parse.urlsplit(redirect_uri)
        callback_target = callback._replace(query="", fragment="")
        if callback.fragment or callback_target != expected_redirect:
            raise ValueError(
                "OAuth callback URL does not match the configured redirect."
            )

        try:
            parameters = parse.parse_qs(
                callback.query,
                keep_blank_values=True,
                strict_parsing=True,
                max_num_fields=10,
            )
        except ValueError as error:
            raise ValueError("OAuth callback query is invalid.") from error

        duplicate = next(
            (name for name, values in parameters.items() if len(values) != 1),
            None,
        )
        if duplicate is not None:
            raise ValueError(f"OAuth callback parameter '{duplicate}' is duplicated.")

        if "error" in parameters:
            oauth_error = parameters["error"][0] or "unknown_error"
            raise ValueError(f"OAuth authorization failed: {oauth_error}.")

        returned_state = _single_value(parameters, "state")
        if not returned_state:
            raise ValueError("No OAuth state found in the callback URL.")
        if not secrets.compare_digest(
            returned_state.encode(),
            expected_state.encode(),
        ):
            raise ValueError("OAuth state does not match the authorization request.")

        code = _single_value(parameters, "code")
        if not code:
            raise ValueError("No authorization code found in the URL")
        return code


def _single_value(parameters: dict[str, list[str]], name: str) -> str | None:
    values = parameters.get(name)
    return values[0] if values else None


def _absolute_url(value: object, *, label: str) -> parse.SplitResult:
    if not isinstance(value, str):
        raise TypeError(f"{label} must be a string.")
    parsed = parse.urlsplit(value)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"{label} must be absolute.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError(f"{label} cannot contain credentials.")
    if parsed.query or parsed.fragment:
        raise ValueError(f"{label} cannot contain a query or fragment.")
    return parsed
