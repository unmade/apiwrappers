========
Overview
========

.. start-badges

.. image:: https://github.com/unmade/apiwrappers/workflows/lint%20and%20test/badge.svg?branch=master
    :alt: Build Status
    :target: https://github.com/unmade/apiwrappers/blob/master/.github/workflows/lint-and-test.yml

.. image:: https://codecov.io/gh/unmade/apiwrappers/branch/master/graph/badge.svg
    :alt: Coverage Status
    :target: https://codecov.io/gh/unmade/apiwrappers

.. image:: http://www.mypy-lang.org/static/mypy_badge.svg
    :alt: Checked with mypy
    :target: http://mypy-lang.org/

.. image:: https://img.shields.io/pypi/v/apiwrappers.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/apiwrappers

.. image:: https://img.shields.io/pypi/pyversions/apiwrappers.svg
    :alt: Supported versions
    :target: https://pypi.org/project/apiwrappers

.. image:: https://img.shields.io/badge/License-MIT-purple.svg
    :alt: MIT License
    :target: https://github.com/unmade/apiwrappers/blob/master/LICENSE

.. end-badges

----------

*apiwrappers* is a library for building API clients
that work both with regular and async code.

Features
========

- **DRY** - support both sync and async implementations with one wrapper
- **Unified interface** - work with different python HTTP client libraries
  in the same way. Currently it supports:

    - `requests <https://requests.readthedocs.io/en/master/>`_
    - `aiohttp <https://docs.aiohttp.org/en/stable/client.html>`_

- **Customizable** - middleware mechanism to customize request/response
- **Typed** - library is fully typed and it is relatively easy
  to get fully type annotated wrapper

Installation
============

.. code-block:: bash

    pip install apiwrappers[requests,aiohttp]

*Note: extras are optional and mainly needed for the final
user of your future API wrapper*

Quickstart
==========

Each wrapper needs a HTTP client to make requests to the API.

*apiwrappers* provides common interface (drivers) for
the most popular HTTP clients.
Let's learn how to make a simple request:

.. code-block:: python

    >>> from apiwrappers import Method, Request, make_driver
    >>> request = Request(Method.GET, "https://example.org", "/")
    >>> driver = make_driver("requests")
    >>> response = driver.fetch(request)
    >>> response
    <Response [200]>
    >>> response.status_code
    200
    >>> response.headers["content-type"]
    'text/html; charset=UTF-8'
    >>> response.text()
    '<!doctype html>\n<html>\n<head>\n<title>Example Domain</title>...'

Or using asynchronous driver:

*Use IPython or Python 3.8+ with python -m asyncio
to try this code interactively*

.. code-block:: python

    >>> from apiwrappers import Method, Request, make_driver
    >>> request = Request(Method.GET, "https://example.org", "/")
    >>> driver = make_driver("aiohttp")
    >>> response = await driver.fetch(request)
    >>> response
    <Response [200]>

Writing a simple API client
----------------------------

Now, that we learned how to make HTTP requests,
let's build our first API client:

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
        def get_repos(self: "Github[Driver]", username: str) -> List[Repo]:
            ...

        @overload
        def get_repos(self: "Github[AsyncDriver]", username: str) -> Awaitable[List[Repo]]:
            ...

        def get_repos(self, username: str):
            request = Request(Method.GET, self.host, f"/users/{username}/repos")
            return fetch(self.driver, request, model=List[Repo])

Here we defined ``Repo`` dataclass that describes what we want
to get from response and pass it to the ``fetch`` function.

The API client is ready for use:

.. code-block:: python

    >>> from apiwrappers import make_driver
    >>> driver = make_driver("requests")
    >>> github = Github("https://api.github.com", driver=driver)
    >>> github.get_repos("unmade")
    [Repo(id=47463599, name='am-date-picker'),
     Repo(id=231653904, name='apiwrappers'),
     Repo(id=144204778, name='conway'),
     ...
    ]

To use it with asyncio all we need to do is provide a proper driver
and don't forget to ``await`` method call:

.. code-block:: python

    >>> from apiwrappers import make_driver
    >>> driver = make_driver("aiohttp")
    >>> github = Github("https://api.github.com", driver=driver)
    >>> await github.get_repos("unmade")
    [Repo(id=47463599, name='am-date-picker'),
     Repo(id=231653904, name='apiwrappers'),
     Repo(id=144204778, name='conway'),
     ...
    ]

Experimental Features
---------------------

As experiment, there is also a ``Fetch`` descriptor.
``Fetch`` helps reduce boilerplate and lets you write wrappers
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
            return Request(Method.GET, self.host, f"/users/{username}/repos")

Here we did the following:

#. First, we defined ``Repo`` dataclass that describes what
   we want to get from response
#. Next, we used ``Fetch`` descriptor to declare API method
#. Each ``Fetch`` object also needs a so-called request factory.
   We provide one by using ``get_repos.request`` decorator
   on the ``get_repos_request``
#. ``get_repos_request`` is a pure function and easy to test
#. No need to use overload - mypy will understand the return type
   of the ``.get_repos`` call, but not the signature (due to limited
   support of the callable argument)
