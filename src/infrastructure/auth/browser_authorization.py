import webbrowser
from dataclasses import dataclass
from urllib import parse


@dataclass(frozen=True, slots=True)
class StravaAuthorizationConfig:
    """Configuration required to start Strava's browser authorization flow."""

    client_id: str
    authorization_url: str = "https://www.strava.com/oauth/authorize"
    redirect_uri: str = "http://localhost/exchange_token"
    scope: str = "read,read_all,activity:read,activity:read_all"

    def __post_init__(self) -> None:
        if not self.client_id:
            raise ValueError("Strava client ID cannot be empty.")

    def as_query_params(self) -> dict[str, str]:
        return {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "approval_prompt": "force",
            "scope": self.scope,
        }


class BrowserAuthorizationCodeProvider:
    """Obtain an OAuth code through the user's default browser."""

    def __init__(self, config: StravaAuthorizationConfig) -> None:
        self._config = config

    def get_authorization_code(self) -> str:
        auth_url = self._create_full_url(
            self._config.authorization_url,
            self._config.as_query_params(),
        )
        webbrowser.open(auth_url)
        print("Paste here the URL from the browser: ", end="")
        return self._extract_code(input().strip())

    @staticmethod
    def _create_full_url(base_url: str, params: dict[str, str]) -> str:
        url_parts = list(parse.urlparse(base_url))
        url_parts[4] = parse.urlencode(params)
        return parse.urlunparse(url_parts)

    @staticmethod
    def _extract_code(url: str) -> str:
        values = parse.parse_qs(parse.urlparse(url).query).get("code")
        if not values or not values[0]:
            raise ValueError("No authorization code found in the URL")
        return values[0]
