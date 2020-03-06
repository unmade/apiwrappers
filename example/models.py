from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    login: str
    url: str
    avatar_url: str


@dataclass
class UserDetail(User):
    name: str
    email: Optional[str]


@dataclass
class Me(UserDetail):
    total_private_repos: int
    owned_private_repos: int
    two_factor_authentication: bool
