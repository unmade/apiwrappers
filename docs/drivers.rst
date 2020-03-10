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

You can create them with a :py:func:`make_driver() <apiwrappers.make_driver>`
factory. Let's learn how to make a simple request using a driver
for `requests <https://requests.readthedocs.io/en/master/>`_ library:

.. code-block:: python

    >>> from apiwrappers import Request, make_driver
    >>> driver = make_driver("requests")
    >>> request = Request("GET", "https://example.org")
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

    >>> from apiwrappers import Request, make_driver
    >>> driver = make_driver("aiohttp")
    >>> request = Request("GET", "https://example.org")
    >>> response = await driver.fetch(request)
    >>> response
    <Response [200]>

As you see, some drivers can be used regularly, while others - asynchronously.
It is also better to think of what structural protocol particular driver
follows, rather than what library it uses underneath.

Driver protocols
================

All drivers should follow either :py:class:`Driver <apiwrappers.Driver>`
or :py:class:`AsyncDriver <apiwrappers.AsyncDriver>` protocols, depending on
which HTTP client is used.Protocols also help to abstract away from concrete
driver implementations and ease type checking and annotation.

Timeouts
========

You can set timeouts in seconds when creating a driver or
when making a request. The later will take precedences over driver settings.

By default timeout is ``5 minutes``.

Here is how you can change it:

.. code-block:: python

    from apiwrappers import make_driver

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

You can enable/disable SSL verification or provide custom SSL certs
upon driver instantiation. Default CA bundle provided by
`certifi <https://github.com/certifi/python-certifi>`_ library.

By default SSL verification is enabled.

Here is how you can change it:

.. code-block:: python

    from apiwrappers import make_driver

    # disable SSL verification
    driver = make_driver("requests", verify=False)

    # custom SSL with trusted CAs
    driver = make_driver("requests", verify="/path/to/ca-bundle.crt")

    # custom Client Side Certificates
    certs = ('/path/to/client.cert', '/path/to/client.key')
    driver = make_driver("requests", cert=certs)

Writing your own driver
=======================

To write a driver you don't need to subclass anything
and have a lot of freedom. You can write however you want,
the key thing is to follow one of the protocols.

.. toctree::
   :name: drivers
