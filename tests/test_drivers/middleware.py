from apiwrappers import Request, Response
from apiwrappers.middleware import BaseMiddleware


class RequestMiddleware(BaseMiddleware):
    def process_request(self, request: Request) -> Request:
        request.headers = {"Request-Middleware": "request_middleware"}
        return super().process_request(request)


class ResponseMiddleware(BaseMiddleware):
    def process_response(self, response: Response) -> Response:
        response.headers.update({"Response-Middleware": "response_middleware"})
        return super().process_response(response)
