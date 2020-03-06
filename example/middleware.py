import logging

from apiwrappers import Request, Response, utils
from apiwrappers.middleware import BaseMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    def process_request(self, request: Request) -> Request:
        logger.info("Request: %s %s", request.method, self._url(request))
        return super().process_request(request)

    def process_response(self, response: Response) -> Response:
        logger.info("Response: %s %s", response.status_code, response.url)
        return super().process_response(response)

    def process_exception(self, request, exception):
        url = self._url(request)
        logger.exception("Response: %s %s: %s", request.method, url, exception)
        return super().process_exception(request, exception)

    @staticmethod
    def _url(request: Request) -> str:
        return utils.build_url(request.host, request.path)
