# pylint: disable=unused-import

import sys

if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol  # noqa: F401 pylint: disable=no-name-in-module
