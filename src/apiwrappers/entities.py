# pylint: disable=too-many-instance-attributes

from __future__ import annotations

import enum
import json
from dataclasses import dataclass
from http.cookies import SimpleCookie
from typing import Any, MutableMapping, Union, cast

from apiwrappers.structures import CaseInsensitiveDict, Url
from apiwrappers.typedefs import JSON, Auth, Data, Files, QueryParams


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
        url: URL to send request to.
        query_params: dictionary or list of tuples to send in the query string. Param
            with None values will not be added to the query string. Default value is
            empty dict.
        headers: headers to send.
        cookies: cookies to send.
        auth: Auth tuple to enable Basic Auth or callable returning dict with
            authorization headers, e.g. '{"Authorization": "Bearer ..."}'
        data: the body to attach to the request. If a dictionary or list of tuples
            ``[(key, value)]`` is provided, form-encoding will take place.
        files: Dictionary of ``'name': file-like-objects`` (or ``{'name': file-tuple}``)
            for multipart encoding upload.
            ``file-tuple`` can be a 2-tuple ``('filename', fileobj)``,
            3-tuple ``('filename', fileobj, 'content_type')``, where ``'content-type'``
            is a string defining the content type of the given file.
        json: json for the body to attach to the request (mutually exclusive with
            ``data`` arg).

    Raises:
        ValueError: If both ``data`` or ``files`` or ``json`` args provided.

    Usage::

        >>> from apiwrappers import Request
        >>> Request(Method.GET, 'https://example.org')
        Request(method=<Method.GET: 'GET'>, ...)
    """

    method: Method
    url: Url
    query_params: QueryParams
    headers: MutableMapping[str, str]
    cookies: MutableMapping[str, str]
    auth: Auth = None
    data: Data = None
    files: Files = None
    json: JSON = None

    def __init__(
        self,
        method: Union[str, Method],
        url: Union[str, Url],
        query_params: QueryParams = None,
        headers: MutableMapping[str, str] = None,
        cookies: MutableMapping[str, str] = None,
        auth: Auth = None,
        data: Data = None,
        files: Files = None,
        json: JSON = None,
    ):
        # pylint: disable=redefined-outer-name,too-many-arguments
        if sum((data is not None, files is not None, json is not None)) > 1:
            raise ValueError(
                "`data`, `files` and `json` parameters are mutually exclusive"
            )

        self.method = Method(method)
        self.url = Url(url) if isinstance(url, str) else url
        self.query_params = query_params or {}
        self.headers = headers or {}
        self.cookies = cookies or {}
        self.auth = auth
        self.data = data
        self.files = files
        self.json = json

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
