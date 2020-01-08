from http.cookies import SimpleCookie

import requests

from apiwrappers import utils
from apiwrappers.entities import Request, Response, Timeout
from apiwrappers.structures import CaseInsensitiveDict

DEFAULT_TIMEOUT = 5 * 60  # 5 minutes


class RequestsDriver:
    def __init__(self, timeout: Timeout = DEFAULT_TIMEOUT):
        self.timeout = timeout

    def fetch(self, request: Request, timeout: Timeout = None) -> Response:
        response = requests.request(
            request.method.value,
            utils.build_url(request.host, request.path),
            params=request.query_params,
            headers=request.headers,
            cookies=request.cookies,
            data=request.data,
            json=request.json,
            timeout=self._prepare_timeout(timeout),
        )

        def text():
            return response.text

        return Response(
            status_code=int(response.status_code),
            url=response.url,
            headers=CaseInsensitiveDict(response.headers),
            cookies=SimpleCookie(response.cookies),
            content=response.content,
            text=text,
            json=response.json,
        )

    def _prepare_timeout(self, timeout: Timeout) -> Timeout:
        return timeout or self.timeout
