# pylint: disable=too-many-instance-attributes

import enum
import json
from dataclasses import dataclass, field
from http.cookies import SimpleCookie
from typing import Any, Mapping, Optional, Tuple, cast

from apiwrappers.structures import CaseInsensitiveDict
from apiwrappers.typedefs import JSON, Data, QueryParams


class Method(enum.Enum):
    """
    A subclass of enum.Enum that defines a set of HTTP methods

    The available methods are:
        * DELETE
        * HEAD
        * GET
        * POST
        * PUT
        * PATCH

    Usage::

        >>> from apiwrappers import Method
        >>> Method.GET
        <Method.GET: 'GET'>
        >>> Method.POST == 'POST'
        True

    """

    DELETE = "DELETE"
    HEAD = "HEAD"
    GET = "GET"
    PATCH = "PATCH"
    POST = "POST"
    PUT = "PUT"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            value = str(self.value)  # see: https://github.com/PyCQA/pylint/issues/2306
            return value == other.upper()
        return super().__eq__(other)

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} [{self.value}]>"


@dataclass
class Request:
    """
    A container holding a request information

    Args:
        method: HTTP Method to use.
        host: host name of the resource with scheme.
        path: path to a resource.
        query_params: dictionary or list of tuples to send in the query string. Param
            with None values will not be added to the query string. Default value is
            empty dict.
        headers: headers to send.
        cookies: cookies to send.
        auth: Auth tuple to enable Basic Auth.
        data: the body to attach to the request. If a dictionary or list of tuples
            ``[(key, value)]`` is provided, form-encoding will take place.
        json: json for the body to attach to the request (mutually exclusive with
            ``data`` arg)

    Raises:
        ValueError: If both ``data`` and ``json`` args provided

    Usage::

        >>> from apiwrappers import Request
        >>> Request(Method.GET, 'https://example.org', '/')
        Request(method=<Method.GET: 'GET'>, ...)
    """

    method: Method
    host: str
    path: str
    query_params: QueryParams = field(default_factory=dict)
    headers: Mapping[str, str] = field(default_factory=dict)
    cookies: Mapping[str, str] = field(default_factory=dict)
    auth: Optional[Tuple[str, str]] = None
    data: Data = None
    json: JSON = None

    def __post_init__(self):
        if self.data is not None and self.json is not None:
            raise ValueError("`data` and `json` parameters are mutually exclusive")

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} [{self.method.value}]>"


@dataclass
class Response:
    """
    A container holding a response from server.

    Args:
        request: request object to which this is a response.
        status_code: integer Code of responded HTTP Status, e.g. 404 or 200.
        url: final URL location of Response
        headers: case-insensitive dict of response headers. For example,
            ``headers['content-encoding']`` will return the value of a
            ``'Content-Encoding'`` response header.
        cookies: cookies the server sent back.
        content: content of the response, in bytes.
        encoding: encoding or the response.
    """

    request: Request
    status_code: int
    url: str
    headers: CaseInsensitiveDict[str]
    cookies: SimpleCookie
    content: bytes
    encoding: str

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} [{self.status_code}]>"

    def text(self) -> str:
        """
        Returns content of the response, in unicode.

        If server response doesn't specified encoding, ``utf-8`` will be used instead.
        """
        return self.content.decode(self.encoding)

    def json(self) -> JSON:
        """
        Returns the json-encoded content of the response.

        Raises:
             ValueError: if the response body does not contain valid json.
        """
        return cast(JSON, json.loads(self.content.decode(self.encoding)))
