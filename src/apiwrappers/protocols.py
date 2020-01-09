from apiwrappers.compat import Protocol
from apiwrappers.entities import AsyncResponse, Request, Response
from apiwrappers.typedefs import Timeout


class Driver(Protocol):
    timeout: Timeout

    def fetch(self, request: Request) -> Response:
        ...


class AsyncDriver(Protocol):
    timeout: Timeout

    async def fetch(self, request: Request) -> AsyncResponse:
        ...
