# pylint: skip-file

from __future__ import annotations

import logging
from typing import Awaitable, Generic, List, Optional, TypeVar, overload

from example.middleware import LoggingMiddleware
from example.models import Me, User, UserDetail

from apiwrappers import AsyncDriver, Driver, Method, Request, fetch, make_driver
from apiwrappers.typedefs import Auth

T = TypeVar("T", Driver, AsyncDriver)


class GitHub(Generic[T]):
    def __init__(self, host: str, driver: T, auth: Auth = None):
        self.host = host
        self.driver: T = driver
        self.auth = auth

    @overload
    def users(self: GitHub[Driver], since: int = 0) -> List[User]:
        ...

    @overload
    def users(self: GitHub[AsyncDriver], since: int = 0) -> Awaitable[List[User]]:
        ...

    def users(self, since: int = 0):
        """
        Lists all users, in the order that they signed up on GitHub.

        Pagination is powered exclusively by the since parameter.

        Args:
            since: The integer ID of the last User that you've seen.

        Returns:
            List of GitHub users
        """
        params = {"since": str(since)}
        request = Request(Method.GET, self.host, "/users", query_params=params)
        return fetch(self.driver, request, model=List[User])

    @overload
    def user(self: GitHub[Driver], username: str) -> UserDetail:
        ...

    @overload
    def user(self: GitHub[AsyncDriver], username: str) -> UserDetail:
        ...

    def user(self, username: str):
        """
        Provides publicly available information about someone with a GitHub account.

        Args:
            username: User's username on the GitHub

        Returns:
            Public profile information for GitHub User.
        """
        # url = url_factory(self.host, "/users/{username}", username=username)
        # url = Url(self.host, "/users/{username}", username=username)
        request = Request(Method.GET, self.host, f"/users/{username}")
        # reveal_type(request.method)
        return fetch(self.driver, request, model=UserDetail)

    @overload
    def me(self: GitHub[Driver]) -> Me:
        ...

    @overload
    def me(self: GitHub[AsyncDriver]) -> Awaitable[Me]:
        ...

    def me(self):
        """
        Lists public and private profile information when authenticated through
        basic auth or OAuth with the user scope.

        Returns:
            Public and private profile information for currently authenticated user.
        """
        assert self.auth is not None, "`auth` must be set for this method"
        request = Request(Method.GET, self.host, "/user", auth=self.auth)
        return fetch(self.driver, request, model=Me)

    @overload
    def update_me(
        self: GitHub[Driver], name: Optional[str] = None, email: Optional[str] = None
    ) -> Me:
        ...

    @overload
    def update_me(
        self: GitHub[AsyncDriver],
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Awaitable[Me]:
        ...

    def update_me(self, name: Optional[str] = None, email: Optional[str] = None):
        """
        Update private profile information when authenticated through
        basic auth or OAuth with the user scope.

        If your email is set to private and you send an email parameter as part of this
        request to update your profile, your privacy settings are still enforced:
        the email address will not be displayed on your public profile or via the API.

        Args:
            name: The new name of the user.
            email: The publicly visible email address of the user.

        Returns:
            Public and private profile information for currently authenticated user.
        """
        assert self.auth is not None, "`auth` must be set for this method"
        data = {k: v for k, v in vars().items() if v is not None}
        assert data, "At least one field to update must be provided"
        request = Request(Method.PATCH, self.host, "/user", json=data, auth=self.auth)
        return fetch(self.driver, request, model=Me)


if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.DEBUG)
    creds = ("username", "password_or_token")
    driver = make_driver("requests", LoggingMiddleware)
    github = GitHub("https://api.github.com", driver=driver, auth=creds)
    github.me()
