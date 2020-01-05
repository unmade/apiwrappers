import requests

from apiwrappers import utils
from apiwrappers.entities import Request, Response


class RequestsDriver:
    def fetch(self, request: Request) -> Response:  # pylint: disable=no-self-use
        response = requests.request(
            request.method.value,
            utils.build_url(request.host, request.path),
            data=request.data,
            json=request.json,
            timeout=request.timeout,
            verify=request.verify_ssl,
        )

        def text():
            return response.text

        return Response(
            status_code=int(response.status_code),
            url=response.url,
            content=response.content,
            text=text,
            json=response.json,
        )
