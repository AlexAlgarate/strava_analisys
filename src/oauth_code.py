import re
import webbrowser
from typing import Dict
from urllib import parse


class OAuthHelper:
    """Gestiona el flujo para obtener el código de autorización."""

    @staticmethod
    def _create_full_url(base_url: str, params: Dict[str, str]) -> str:
        url_parts = list(parse.urlparse(base_url))
        query_string = parse.urlencode(params)
        url_parts[4] = query_string
        return parse.urlunparse(url_parts)

    @staticmethod
    def _extract_code(url: str) -> str:
        full_code = re.search(r"&code=([\w]+)&", url)
        if not full_code:
            raise ValueError("No authorization code found in the URL.")
        return full_code.group(1)

    def get_authorization_code(self, base_url: str, params: Dict[str, str]) -> str:
        auth_url = self._create_full_url(base_url, params)
        webbrowser.open(auth_url)
        print("Paste here the URL from the browser: ", end="")
        raw_url = input().strip()
        return self._extract_code(raw_url)
