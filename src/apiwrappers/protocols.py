import sys

from apiwrappers.entities import AsyncResponse, Request, Response

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol  # pylint: disable=no-name-in-module


class Driver(Protocol):
    def fetch(self, request: Request) -> Response:
        ...


class AsyncDriver(Protocol):
    async def fetch(self, request: Request) -> AsyncResponse:
        ...
