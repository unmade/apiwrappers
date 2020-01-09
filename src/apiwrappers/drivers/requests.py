from http.cookies import SimpleCookie
from typing import Union

import requests

from apiwrappers import utils
from apiwrappers.entities import Request, Response
from apiwrappers.structures import CaseInsensitiveDict
from apiwrappers.typedefs import Timeout
from apiwrappers.utils import NoValue

DEFAULT_TIMEOUT = 5 * 60  # 5 minutes


class RequestsDriver:
    def __init__(self, timeout: Timeout = DEFAULT_TIMEOUT, verify_ssl: bool = True):
        self.timeout = timeout
        self.verify_ssl = verify_ssl

    def fetch(
        self,
        request: Request,
        timeout: Timeout = None,
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        response = requests.request(
            request.method.value,
            utils.build_url(request.host, request.path),
            params=request.query_params,
            headers=request.headers,
            cookies=request.cookies,
            data=request.data,
            json=request.json,
            timeout=self._prepare_timeout(timeout),
            verify=self._prepare_ssl(verify_ssl),
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

    def _prepare_ssl(self, verify_ssl: Union[bool, NoValue]) -> bool:
        if isinstance(verify_ssl, bool):
            return verify_ssl
        return self.verify_ssl
