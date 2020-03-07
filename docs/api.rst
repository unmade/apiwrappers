.. toctree::
   :name: api

=======================
API Reference
=======================

.. automodule:: apiwrappers

This page is reference for the public API.
Each class or function can be imported directly from **apiwrappers**.

.. autofunction:: fetch
.. autofunction:: make_driver

Driver Protocols
----------------

.. autoclass:: AsyncDriver
    :members: fetch
.. autoclass:: Driver
    :members: fetch

Request and Response
--------------------

.. autoclass:: Method
.. autoclass:: Request
.. autoclass:: Response
    :members: text, json
.. autoclass:: Url
    :members: __call__

Exceptions
----------

.. autoexception:: DriverError
.. autoexception:: ConnectionFailed
.. autoexception:: Timeout
