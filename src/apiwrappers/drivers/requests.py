import ssl
from http.cookies import SimpleCookie
from typing import Type, Union

import requests
import requests.exceptions

from apiwrappers import exceptions, utils
from apiwrappers.entities import Request, Response
from apiwrappers.middleware import MiddlewareChain
from apiwrappers.middleware.auth import Authentication
from apiwrappers.protocols import Middleware
from apiwrappers.structures import CaseInsensitiveDict, NoValue
from apiwrappers.typedefs import ClientCert, Timeout, Verify

DEFAULT_TIMEOUT = 5 * 60  # 5 minutes


class RequestsDriver:
    middleware = MiddlewareChain(Authentication)

    def __init__(
        self,
        *middleware: Type[Middleware],
        timeout: Timeout = DEFAULT_TIMEOUT,
        verify: Verify = True,
        cert: ClientCert = None,
    ):
        self.middleware = middleware
        self.timeout = timeout
        self.verify = verify
        self.cert = cert

    def __repr__(self) -> str:
        middleware = [m.__name__ for m in self.middleware]
        if middleware:
            middleware.append("")
        return (
            f"{self.__class__.__name__}("
            f"{', '.join(middleware)}"
            f"timeout={self.timeout}, "
            f"verify={self.verify}"
            ")"
        )

    def __str__(self) -> str:
        return "<Driver 'requests'>"

    @middleware.wrap
    def fetch(
        self, request: Request, timeout: Union[Timeout, NoValue] = NoValue(),
    ) -> Response:
        try:
            response = requests.request(
                request.method.value,
                utils.build_url(request.host, request.path),
                params=request.query_params,
                headers=request.headers,
                cookies=request.cookies,
                data=request.data,
                files=request.files,
                json=request.json,
                timeout=self._prepare_timeout(timeout),
                verify=self.verify,
                cert=self.cert,
            )
        except requests.Timeout as exc:
            raise exceptions.Timeout from exc
        except requests.exceptions.SSLError as exc:
            raise ssl.SSLError(str(exc)) from exc
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
