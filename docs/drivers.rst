.. _drivers-page:

=======
Drivers
=======

Drivers are essentially adapters for different python HTTP client libraries.

This page will walk you through the concept of drivers
in the *apiwrappers* library.

Basic Usage
===========

Out of the box *apiwrappers* provides drivers for
`requests <https://requests.readthedocs.io/en/master/>`_ and
`aiohttp <https://docs.aiohttp.org/en/stable/client.html>`_
libraries.

You can create them with a ``make_driver`` factory.
Let's learn how to make a simple request using a driver
for `requests <https://requests.readthedocs.io/en/master/>`_ library:

.. code-block:: python

    >>> from apiwrappers import Method, Request, make_driver
    >>> driver = make_driver("requests")
    >>> request = Request(Method.GET, "https://example.org", "/")
    >>> response = driver.fetch(request)
    >>> response
    <Response [200]>
    >>> response.status_code
    200
    >>> response.headers["content-type"]
    'text/html; charset=UTF-8'
    >>> response.text()
    '<!doctype html>\n<html>\n<head>\n<title>Example Domain...'

Or using driver for `aiohttp <https://docs.aiohttp.org/en/stable/client.html>`_:

*Use IPython or Python 3.8+ with python -m asyncio
to try this code interactively*

.. code-block:: python

    >>> from apiwrappers import Method, Request, make_driver
    >>> driver = make_driver("aiohttp")
    >>> request = Request(Method.GET, "https://example.org", "/")
    >>> response = await driver.fetch(request)
    >>> response
    <Response [200]>

As you see, some drivers can be used regularly, while others - asynchronously.
It is also better to think of what structural protocol particular driver
follows, rather than what library it uses underneath.

Driver protocols
================

All drivers should follow either `Driver` or `AsyncDriver` protocols,
depending on which HTTP client is used.
Protocols also help to abstract away from concrete driver implementations
and ease type checking and annotation.

Driver
------

To be compliant with ``Driver`` protocol
driver should have this fields and methods:

.. code-block:: python

        timeout: Timeout
        verify_ssl: bool
        middleware: List[Type[Middleware]]

        def fetch(
            self,
            request: Request,
            timeout: Union[Timeout, NoValue] = NoValue(),
            verify_ssl: Union[bool, NoValue] = NoValue(),
        ) -> Response:
            ...

AsyncDriver
-----------

To be compliant with ``AsyncDriver`` protocol
driver should have this fields and methods:

.. code-block:: python

    timeout: Timeout
    verify_ssl: bool
    middleware: List[Type[AsyncMiddleware]]

    async def fetch(
        self,
        request: Request,
        timeout: Union[Timeout, NoValue] = NoValue(),
        verify_ssl: Union[bool, NoValue] = NoValue(),
    ) -> Response:
        ...

Timeouts
========

You can set timeouts in seconds when creating a driver or
when making a request. The later will take precedences over driver settings.

By default timeout is ``5 minutes``.

Here is how you can change it:

.. code-block:: python

    from apiwrappers import Method, Request, make_driver

    driver = make_driver("requests", timeout=5)

    # making a request with timeout set to 5 seconds
    driver.fetch(request)

    # making a request with timeout set to 2.5 seconds
    driver.fetch(request, timeout=2.5)

    # timeout is disabled, wait infinitely
    driver.fetch(request, timeout=None)

In case timeout value is exceeded ``Timeout`` error will be raised

SSL Verification
================

You can enable/disable SSL verification when creating a driver or
when making a request. The later will take precedences over driver settings.

By default SSL verification is enabled.

Here is how you can change it:

.. code-block:: python

    from apiwrappers import Method, Request, make_driver

    # disable SSL verification
    driver = make_driver("requests", verify_ssl=False)

    # making a request without SSL verification
    driver.fetch(request)

    # making a request with SSL verification
    driver.fetch(request, verify_ssl=True)

Writing your own driver
=======================

To write a driver you don't need to subclass anything
and have a lot of freedom. You can write however you want,
the key thing is to follow one of the protocols.

.. toctree::
   :name: drivers
