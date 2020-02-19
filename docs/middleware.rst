.. toctree::
   :name: middleware

==========
Middleware
==========

Middleware is a light "plugin" system for altering driver's
request/response/exception processing.

This page will walk you through the concept of middleware
in the *apiwrappers* library.

Writing your own middleware
===========================

A middleware factory is a callable that takes a callable and returns
a middleware. A middleware is a callable that takes same argument as
``driver.fetch`` and returns a response.

The most simple way is to write a middleware as function:

.. code-block:: python

    from apiwrappers.structures import NoValue


    def simple_middleware(handler):

        def middleware(
            request, timeout=NoValue(), verify_ssl=NoValue()
        ):
            # Code to be executed before request is made
            response = handler(request, timeout, verify_ssl)
            # Code to be executed after request is made
            return response

        return middleware

Since middleware is used by drivers, and the one we've written can be used
only by regular driver, we also need to provide an async implementation:

.. code-block:: python

    from apiwrappers.structures import NoValue


    def simple_async_middleware(handler):

        async def middleware(
            request, timeout=NoValue(), verify_ssl=NoValue()
        ):
            # Code to be executed before request is made
            response = await handler(request, timeout, verify_ssl)
            # Code to be executed after request is made
            return response

        return middleware

As you can see, the only difference is that in async middleware we have to
await the handler call.

To help us reduce this code duplication *apiwrappers* provides a
``BaseMiddleware`` class. Subclassing one you can then
override it hook methods like that:

.. code-block:: python

    from typing import NoReturn

    from apiwrappers import Request, Response
    from apiwrappers.middleware import BaseMiddleware


    class SimpleMiddleware(BaseMiddleware):
        def process_request(self, request: Request) -> Request:
            # Code to be executed before request is made
            return request

        def process_response(self, response: Response) -> Response:
            # Code to be executed after request is made
            return response

        def process_exception(
            self, request: Request, exception: Exception
        ) -> NoReturn:
            # Code to be executed when any exception is raised
            raise exception

Using middleware
================

Middleware are used by drivers and each driver accepts a list of middleware.

Although, middleware we defined earlier literally does nothing,
it still can be used like that:

.. code-block:: python

    from apiwrappers import make_driver


    driver = make_driver("requests", SimpleMiddleware)
    # RequestsDriver(Authorization, SimpleMiddleware, ...)

*Note, that even we provide only ``SimpleMiddleware`` the driver also has
``Authorization`` middleware. That's because some drivers have middleware
that should always be present.*

You can also change driver middleware after creation by simply reassigning
``driver.middleware`` attribute:

.. code-block:: python

    driver.middleware = []
    # RequestsDriver(Authorization, ...)

The order of the default middleware can be overridden by explicitly
specifying it:

.. code-block:: python

    driver.middleware = [SimpleMiddleware, Authorization]
    # RequestsDriver(SimpleMiddleware, Authorization, ...)

Middleware order
================

The order of middleware matters because a middleware can depend on other
middleware.

Before making actual request, middleware are executed in the order
they are defined.
After getting the response middleware are executed in the reverse order.
