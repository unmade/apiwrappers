import logging

from apiwrappers import Request, Response
from apiwrappers.middleware import BaseMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    def process_request(self, request: Request) -> Request:
        logger.info("Request: %s %s", request.method, request.url.template)
        return super().process_request(request)

    def process_response(self, response: Response) -> Response:
        logger.info("Response: %s %s", response.status_code, response.url)
        return super().process_response(response)

    def process_exception(self, request, exception):
        logger.exception("Response: %s %s: %s", request.method, request.url, exception)
        return super().process_exception(request, exception)
