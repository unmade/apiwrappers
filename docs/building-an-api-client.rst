=======================
Building an API Client
=======================

This page will walk you through steps on how to build wrapper for API.

Making a Request
================

Each wrapper needs a HTTP client to make requests to the API.

You can easily use one of the :doc:`drivers <drivers>` to make requests, but
:py:meth:`Driver.fetch() <apiwrappers.Driver.fetch>` call returns a
:py:class:`Response <apiwrappers.Response>` object, which is not always
suitable for building good API clients.

For API client it can be better to return typed data,
such as dataclasses, than let the final user deal with json.

*apiwrappers* provides a :py:func:`fetch() <apiwrappers.fetch>` function,
which takes driver as a first argument, and all other
arguments are the same as with
:py:meth:`Driver.fetch() <apiwrappers.Driver.fetch>`.
Giving that, it behaves exactly like if you are working with driver:

.. code-block:: python

    >>> from apiwrappers import Request, fetch, make_driver
    >>> driver = make_driver("requests")
    >>> request = Request("GET", "https://example.org")
    >>> response = fetch(driver, request)
    <Response [200]>

You can also provide two additional arguments:

- ``model`` - a type or factory function that describes response structure.
- ``source`` - optional key name in the json, which value will be passed
  to the ``model``. You may use dotted notation to traverse keys - ``key1.key2``

With these arguments, :py:func:`fetch() <apiwrappers.fetch>` function acts like
a factory, returning new instance of the type provided to the ``model`` argument:

.. code-block:: python

    from dataclasses import dataclass
    from typing import List

    from apiwrappers import Request, fetch, make_driver

    @dataclass
    class Repo:
        name: str

    url = "https://api.github.com/users/unmade/repos"
    request = Request("GET", url)

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

    from apiwrappers import Request, Url, fetch


    @dataclass
    class Repo:
        id: int
        name: str


    class GitHub:
        def __init__(self, host, driver):
            self.url = Url(host)
            self.driver = driver

        def get_repos(self, username):
            url = self.url("/users/{username}/repos", username=username)
            request = Request("GET", url)
            return fetch(self.driver, request, model=List[Repo])

Here we defined ``.get_repos`` method to get all user's repos.
Based on the driver this method returns either a ``List[Repo]``
or a coroutine - ``Awaitable[List[Repo]]``

*You never want to await the fetch call here,
just return it immediately and let the final user await it if needed*

Another thing to notice is how we create URL:

.. code-block:: python

    url = self.url("/users/{username}/repos", username=username)

Sometimes, it's useful to have an URL template, for example, for logging
or for aggregating metrics, so instead of formatting immediately, we
provide a template and replacement fields.

The wrapper above is good enough to satisfy most cases,
however it lacks one of the important features nowadays - type annotations.

Adding Type Annotations
-----------------------

In the example above, we didn't add any type annotations for
``.get_repos`` method.

We can simply specify return type as:

.. code-block:: python

    Union[List[Repo], Awaitable[List[Repo]]

and that will be enough to have a good auto-completion,
but what we want precise type annotations.

We want to tell mypy, that when driver corresponds to
:py:class:`Driver <apiwrappers.Driver>` protocol
``.get_repos`` has return type ``List[Repo]``
and for :py:class:`AsyncDriver <apiwrappers.AsyncDriver>` protocol -
``Awaitable[List[Repo]]``.

It can be done like that:

.. code-block:: python

    from __future__ import annotations

    from dataclasses import dataclass
    from typing import Awaitable, Generic, List, TypeVar, overload

    from apiwrappers import AsyncDriver, Driver, Request, Url, fetch

    T = TypeVar("T", Driver, AsyncDriver)


    @dataclass
    class Repo:
        id: int
        name: str


    class GitHub(Generic[T]):
        def __init__(self, host: str, driver: T):
            self.url = Url(host)
            self.driver: T = driver

        @overload
        def get_repos(
            self: GitHub[Driver], username: str
        ) -> List[Repo]:
            ...

        @overload
        def get_repos(
            self: GitHub[AsyncDriver], username: str
        ) -> Awaitable[List[Repo]]:
            ...

        def get_repos(self, username: str):
            url = self.url("/users/{username}/repos", username=username)
            request = Request("GET", url)
            return fetch(self.driver, request, model=List[Repo])

Here, we defined a ``T`` type variable, constrained to
:py:class:`Driver <apiwrappers.Driver>`
and :py:class:`AsyncDriver <apiwrappers.AsyncDriver>` protocols.
Our wrapper is now a generic class of that variable.
We also used :py:func:`overload <typing.overload>` with self-type to define return type based on
the driver provided to our wrapper.

Using the API Client
=========================

Here is how we can use our client:

.. code-block:: python

    >>> from apiwrappers import make_driver
    >>> driver = make_driver("requests")
    >>> github = GitHub("https://api.github.com", driver=driver)
    >>> github.get_repos("unmade")
    [Repo(id=47463599, name='am-date-picker'),
     ...
    ]

Or to use it asynchronously:

.. code-block:: python

    >>> from apiwrappers import make_driver
    >>> driver = make_driver("aiohttp")
    >>> github = GitHub("https://api.github.com", driver=driver)
    >>> await github.get_repos("unmade")
    [Repo(id=47463599, name='am-date-picker'),
     ...
    ]

.. toctree::
   :name: building-an-api-client
