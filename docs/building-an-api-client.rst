=======================
Building an API Client
=======================

This page will walk you through steps on how to build wrapper for API

Making a Request
================

Each wrapper needs a HTTP client to make requests to the API.

You can easily use drivers to make requests, but
they return a ``Response`` object, which is not
always suitable for building good API clients.

For API client it can be better to return typed data,
such as dataclass, than let the final user deal with json.

*apiwrappers* provides a ``fetch`` function,
which takes driver as a first argument, and all other
arguments are the same as with ``driver.fetch``.
Giving that, it behaves exactly like in the examples above:

.. code-block:: python

    >>> from apiwrappers import Method, Request, fetch, make_driver
    >>> driver = make_driver("requests")
    >>> request = Request(Method.GET, "https://example.org", "/")
    >>> response = fetch(driver, request)
    <Response [200]>

You can also provide two additional arguments:

- ``model`` - a type or factory function that describes response structure.
- ``source`` - optional, a key name in the json, which value will be passed
  to the ``model``. You may use dotted notation to traverse keys (`key1.key2`)

With these arguments, ``fetch`` function acts like a factory,
returning new instance of the type provided to the ``model`` argument:

.. code-block:: python

    from dataclasses import dataclass
    from typing import List

    from apiwrappers import Method, Request, fetch, make_driver

    @dataclass
    class Repo:
        name: str

    host = "https://api.github.com"
    request = Request(Method.GET, host, "/users/unmade/repos")

    driver = make_driver("requests")
    fetch(driver, request, model=List[Repo])  # [Repo(name='am-date-picker'), ...]
    fetch(driver, request, model=Repo, source="0")  # Repo(name='am-date-picker')
    fetch(driver, request, model=str, source="0.name")  # 'am-date-picker'

    driver = make_driver("aiohttp")
    await fetch(driver, request, model=List[Repo])  # [Repo(name='am-date-picker'), ...]
    await fetch(driver, request, model=Repo, source="0")  # Repo(name='am-date-picker')
    await fetch(driver, request, model=str, source="0.name")  # 'am-date-picker'

Writing a Simple API Client
===========================

Now that we know how to make requests and how to get data from response,
lets write API client class:

.. code-block:: python

    from dataclasses import dataclass
    from typing import List

    from apiwrappers import Method, Request, fetch


    @dataclass
    class Repo:
        id: int
        name: str


    class Github:
        def __init__(self, host, driver):
            self.host = host
            self.driver = driver

        def get_repos(self, username):
            path = f"/users/{username}/repos"
            request = Request(Method.GET, self.host, path)
            return fetch(self.driver, request, model=List[Repo])

*Note: you never want to await the fetch call here,
just return it immediately and let the final user await it if needed*

The wrapper above is good enough to satisfy most cases,
however it lacks one of the important features nowadays - type annotations.

Adding Type Annotations
=======================

In the example above, we didn't add any type annotations for
``.get_repos`` method.

We can simply specify return type as ``Union[List[Repo], Awaitable[List[Repo]]``,
and that will be enough to have a good autocompletion,
but what we want here to do is a little bit trickier.

We want to tell mypy,
that ``.get_repos`` has return type ``List[Repo]`` for all
drivers corresponding to ``Driver`` protocol,
and ``Awaitable[List[Repo]]`` for ``AsyncDriver`` protocol.

It can be done like that:

.. code-block:: python

    from dataclasses import dataclass
    from typing import Awaitable, Generic, List, TypeVar, overload

    from apiwrappers import AsyncDriver, Driver, Method, Request, fetch

    T = TypeVar("T", Driver, AsyncDriver)


    @dataclass
    class Repo:
        id: int
        name: str


    class Github(Generic[T]):
        def __init__(self, host: str, driver: T):
            self.host = host
            self.driver: T = driver

        @overload
        def get_repos(
            self: "Github[Driver]", username: str
        ) -> List[Repo]:
            ...

        @overload
        def get_repos(
            self: "Github[AsyncDriver]", username: str
        ) -> Awaitable[List[Repo]]:
            ...

        def get_repos(self, username: str):
            path = f"/users/{username}/repos"
            request = Request(Method.GET, self.host, path)
            return fetch(self.driver, request, model=List[Repo])

Here, we defined a ``T`` type variable, constrained to
``Driver`` and ``AsyncDriver`` protocols.
Our wrapper is now a generic class of that variable.
We also used ``@overload`` with self-type to define return type based on
the driver provided to our wrapper.

Using the API Client
=========================

Here is how we can use our client:

.. code-block:: python

    >>> from apiwrappers import make_driver
    >>> driver = make_driver("requests")
    >>> github = Github("https://api.github.com", driver=driver)
    >>> github.get_repos("unmade")
    [Repo(id=47463599, name='am-date-picker'),
     ...
    ]

Or to use it asynchronously:

.. code-block:: python

    >>> from apiwrappers import make_driver
    >>> driver = make_driver("aiohttp")
    >>> github = Github("https://api.github.com", driver=driver)
    >>> await github.get_repos("unmade")
    [Repo(id=47463599, name='am-date-picker'),
     ...
    ]

.. toctree::
   :name: building-an-api-client
