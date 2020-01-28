Experimental Features
---------------------

As experiment, there is also a ``Fetch`` descriptor, that
helps reduce boilerplate and lets you write wrappers
in almost declarative way:

.. code-block:: python

    from __future__ import annotations

    from dataclasses import dataclass
    from typing import Any, Generic, List, Mapping, TypeVar

    from apiwrappers import AsyncDriver, Driver, Method, Request
    from apiwrappers.xfeatures import Fetch

    T = TypeVar("T", Driver, AsyncDriver)


    @dataclass
    class Repo:
        id: int
        name: str

    class Github(Generic[T]):
        get_repos = Fetch(List[Repo])

        def __init__(self, host: str, driver: T):
            self.host = host
            self.driver: T = driver

        @get_repos.request
        def get_repos_request(self, username: str) -> Request:
            path = f"/users/{username}/repos"
            return Request(Method.GET, self.host, path)

Here we did the following:

#. First, we defined ``Repo`` dataclass that describes what
   we want to get from response
#. Next, we used ``Fetch`` descriptor to declare API method
#. Each ``Fetch`` object also needs a so-called request factory.
   We provide one by using ``get_repos.request`` decorator
   on the ``get_repos_request`` method
#. ``get_repos_request`` is a pure function and easy to test
#. No need to use overload - mypy will understand the return type
   of the ``.get_repos`` call

There are several trade-offs using this approach:

- no auto-completion when calling a method, which is a really huge flaw.
- mypy won't check the signature of the method due to limited support
  of the callable argument
- for end user it will be hard to understand what's going on and where to
  look in case of any problem

.. toctree::
   :name: experimental-features
