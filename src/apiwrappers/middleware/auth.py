from typing import Generator

from apiwrappers.auth import BasicAuth
from apiwrappers.entities import Request, Response
from apiwrappers.middleware.base import BaseMiddleware
from apiwrappers.protocols import AsyncHandler, Handler


class Authentication(BaseMiddleware):
    def call_next(
        self, handler: Handler, request: Request, *args, **kwargs,
    ) -> Response:
        gen = self.set_auth_headers(request)
        try:
            while True:
                auth_request = next(gen)
                auth_response = super().call_next(
                    handler, auth_request, *args, **kwargs
                )
                gen.send(auth_response)
        except StopIteration:
            pass
        return super().call_next(handler, request, *args, **kwargs)

    async def call_next_async(
        self, handler: AsyncHandler, request: Request, *args, **kwargs,
    ) -> Response:
        gen = self.set_auth_headers(request)
        try:
            while True:
                auth_request = next(gen)
                auth_response = await super().call_next_async(
                    handler, auth_request, *args, **kwargs
                )
                gen.send(auth_response)
        except StopIteration:
            pass
        return await super().call_next_async(handler, request, *args, **kwargs)

    @staticmethod
    def set_auth_headers(request) -> Generator[Request, Response, None]:
        if request.auth is not None:
            if isinstance(request.auth, tuple):
                request.auth = BasicAuth(*request.auth)
            value = request.auth()
            if isinstance(value, Generator):
                try:
                    while True:
                        auth_response = yield next(value)
                        value.send(auth_response)
                except StopIteration as exc:
                    value = exc.value
            request.headers.update(value)
