import webbrowser
from collections.abc import Mapping
from urllib import parse


class GetOauthCode:
    @staticmethod
    def _create_full_url(base_url: str, params: Mapping[str, str]) -> str:
        url_parts = list(parse.urlparse(base_url))
        query_string = parse.urlencode(params)
        url_parts[4] = query_string
        return parse.urlunparse(url_parts)

    @staticmethod
    def _extract_code(url: str) -> str:
        values = parse.parse_qs(parse.urlparse(url).query).get("code")
        if not values or not values[0]:
            raise ValueError("No authorization code found in the URL")
        return values[0]

    def get_authorization_code(self, base_url: str, params: Mapping[str, str]) -> str:
        auth_url = self._create_full_url(base_url, params)
        webbrowser.open(auth_url)
        print("Paste here the URL from the browser: ", end="")
        raw_url = input().strip()
        return self._extract_code(raw_url)
