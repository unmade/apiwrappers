from http.cookies import SimpleCookie
from typing import List, Type, Union

import requests

from apiwrappers import exceptions, utils
from apiwrappers.entities import Request, Response
from apiwrappers.middleware import apply_middleware
from apiwrappers.protocols import Middleware
from apiwrappers.structures import CaseInsensitiveDict, NoValue
from apiwrappers.typedefs import Timeout

DEFAULT_TIMEOUT = 5 * 60  # 5 minutes


class RequestsDriver:
    def __init__(
        self,
        *middleware: Type[Middleware],
        timeout: Timeout = DEFAULT_TIMEOUT,
        verify_ssl: bool = True,
    ):
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.middleware: List[Type[Middleware]] = list(middleware)

    @apply_middleware
    def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        try:
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
        except requests.Timeout as exc:
            raise exceptions.Timeout from exc
        except requests.ConnectionError as exc:
            raise exceptions.ConnectionFailed from exc
        except requests.RequestException as exc:
            raise exceptions.DriverError from exc

        return Response(
            request=request,
            status_code=int(response.status_code),
            url=response.url,
            headers=CaseInsensitiveDict(response.headers),
            cookies=SimpleCookie(response.cookies),
            encoding=response.encoding or "utf-8",
            content=response.content,
        )

    def _prepare_timeout(self, timeout: Union[Timeout, NoValue]) -> Timeout:
        if isinstance(timeout, NoValue):
            return self.timeout
        return timeout

    def _prepare_ssl(self, verify_ssl: Union[bool, NoValue]) -> bool:
        if isinstance(verify_ssl, NoValue):
            return self.verify_ssl
        return verify_ssl
