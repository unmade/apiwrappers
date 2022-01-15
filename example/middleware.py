import logging

from apiwrappers import Request, Response
from apiwrappers.middleware import BaseMiddleware
from example.exceptions import GitHubException

logger = logging.getLogger(__name__)


class ErrorMiddleware(BaseMiddleware):
    """
    Raises GitHubException for every response with status code 400 and above.
    """

    def process_response(self, response: Response) -> Response:
        if response.status_code >= 400:
            raise GitHubException(response) from None
        return super().process_response(response)


class LoggingMiddleware(BaseMiddleware):
    """
    Logs request/response/exception being made.
    """

    def process_request(self, request: Request) -> Request:
        logger.info("Request: %s %s", request.method, request.url.template)
        return super().process_request(request)

    def process_response(self, response: Response) -> Response:
        logger.info("Response: %s %s", response.status_code, response.url)
        return super().process_response(response)

    def process_exception(self, request, exception):
        logger.exception("Response: %s %s: %s", request.method, request.url, exception)
        return super().process_exception(request, exception)
