.. toctree::
   :name: auth


==============
Authentication
==============

This page describes how you can use various kinds of authentication with
*apiwrappers*.

Basic Authentication
====================

Making request with HTTP Basic Auth is rather straightforward:

.. code-block:: python

    from apiwrappers import Request

    Request(..., auth=("user", "pass"))

Token Authentication
====================

To make a request with a Token Based Authentication:

.. code-block:: python

    from apiwrappers import Request
    from apiwrappers.auth import TokenAuth

    Request(..., auth=TokenAuth("your_token", kind="JWT"))

Api key Authentication
======================

To make a request with a Api key Based Authentication:

.. code-block:: python

    from apiwrappers import Request
    from apiwrappers.auth import ApiKeyAuth

    Request(..., auth=ApiKeyAuth("your_key", header="apikey"))

Custom Authentication
=====================

You can add your own authentication mechanism relatively easy.

If you don't need to make any external calls, then you can define a callable
that returns a dictionary with authorization headers.

For example, this is simple authentication class:

.. code-block:: python

    from typing import Dict


    class ProxyAuth:
        def __call__(self) -> Dict[str, str]:
            return {"Proxy-Authorization": "<type> <credentials>"}

Authentication Flows
--------------------

Sometimes we need to make additional calls to get credentials.

*apiwrappers* allows you to do just that:

.. code-block:: python

    from typing import Generator, Dict

    from apiwrappers import Request, Response


    class CustomAuthFlow:
        def __call__(self) -> Generator[Request, Response, Dict[str, str]]:
            # you can issue as many request as you needed
            # this is how you issue a request
            response = yield Request(...)

            # response is available immediately for processing
            return {"Authorization": response.json()["token"]}

*Note, that a function now is generator function and you can yield as many
request as you needed, but you should always return a dictionary with
authentication headers.*
