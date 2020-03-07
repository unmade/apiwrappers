========
Overview
========

.. start-badges

.. image:: https://github.com/unmade/apiwrappers/workflows/lint%20and%20test/badge.svg?branch=master
    :alt: Build Status
    :target: https://github.com/unmade/apiwrappers/blob/master/.github/workflows/lint-and-test.yml

.. image:: https://readthedocs.org/projects/apiwrappers/badge/?version=latest
    :alt: Documentation Status
    :target: https://apiwrappers.readthedocs.io/en/latest/?badge=latest

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

- **DRY** - support both regular and async code with one implementation
- **Flexible** - middleware mechanism to customize request/response
- **Typed** - library is fully typed and it's relatively easy
  to get fully typed wrappers
- **Modern** - decode JSON with no effort using dataclasses and type annotations
- **Unified interface** - work with different python HTTP client libraries
  in the same way. Currently supported:

    - `requests <https://requests.readthedocs.io/en/master/>`_
    - `aiohttp <https://docs.aiohttp.org/en/stable/client.html>`_

Installation
============

.. code-block:: bash

    pip install apiwrappers[requests,aiohttp]

*Note: extras are optional and mainly needed for the final
user of your future API wrapper*

QuickStart
==========

Making request is rather straightforward:

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
    fetch(driver, request)  # Response(..., status_code=200, ...)
    fetch(driver, request, model=List[Repo])  # [Repo(name='am-date-picker'), ...]

    driver = make_driver("aiohttp")
    await fetch(driver, request)  # Response(..., status_code=200, ...)
    await fetch(driver, request, model=List[Repo])  # [Repo(name='am-date-picker'), ...]

Writing a Simple API Client
---------------------------

With *apiwrappers* you can bootstrap clients for different API
pretty fast and easily.

Here is how a typical API client would look like:

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
        def get_repos(self: Github[Driver], username: str) -> List[Repo]:
            ...

        @overload
        def get_repos(self: Github[AsyncDriver], username: str) -> Awaitable[List[Repo]]:
            ...

        def get_repos(self, username: str):
            url = self.url("/users/{username}/repos", username=username)
            request = Request("GET", url)
            return fetch(self.driver, request, model=List[Repo])

This is small, but fully typed, API client for one of the
`api.github.com <https://api.github.com>`_ endpoints to get all user repos
by username:

Here we defined ``Repo`` dataclass that describes what we want
to get from response and pass it to the ``fetch`` function.
``fetch`` will then make a request and will cast response to that type.

Note how we create URL:

.. code-block:: python

    url = self.url("/users/{username}/repos", username=username)

Sometimes, it's useful to have an URL template, for example, for logging
or for aggregating metrics, so instead of formatting immediately, we
provide a template and replacement fields.

Using the API Client
--------------------

Here how we can use it:

.. code-block:: python

    >>> from apiwrappers import make_driver
    >>> driver = make_driver("requests")
    >>> github = GitHub("https://api.github.com", driver=driver)
    >>> github.get_repos("unmade")
    [Repo(id=47463599, name='am-date-picker'),
     Repo(id=231653904, name='apiwrappers'),
     Repo(id=144204778, name='conway'),
     ...
    ]

To use it with asyncio all we need to do is provide a proper driver
and don't forget to ``await`` method call:

*Use IPython or Python 3.8+ with python -m asyncio
to try this code interactively*

.. code-block:: python

    >>> from apiwrappers import make_driver
    >>> driver = make_driver("aiohttp")
    >>> github = GitHub("https://api.github.com", driver=driver)
    >>> await github.get_repos("unmade")
    [Repo(id=47463599, name='am-date-picker'),
     Repo(id=231653904, name='apiwrappers'),
     Repo(id=144204778, name='conway'),
     ...
    ]

Documentation
=============

Documentation for *apiwrappers* can be found at
`Read The Docs <https://apiwrappers.readthedocs.io/>`_.

Check out `Extended Client Example <example/README.md>`_.

Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

See `contributing guide <CONTRIBUTING.rst>`_ to learn more.

Currently the code and the issues are hosted on GitHub.

The project is licensed under MIT.
