from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, cast

from apiwrappers import Response
from apiwrappers.utils import fromjson


class ErrorCode(str, Enum):
    MISSING = "missing"
    MISSING_FIELD = "missing_field"
    INVALID = "invalid"
    ALREADY_EXISTS = "already_exists"


@dataclass
class Error:
    code: ErrorCode
    resource: str
    field: str


class GitHubException(Exception):
    """
    Base class for representing GitHub client errors.
    """

    def __init__(self, response: Response):
        content = cast(Dict[str, Any], response.json())
        super().__init__(content["message"])
        self.response = response
        self.errors = fromjson(Optional[List[Error]], content.get("errors"))
