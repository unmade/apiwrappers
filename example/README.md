# Example client: GitHub users API

This is advanced example of the client for the GitHub users API.

Use [client.py](client.py) as a reference for the client definition.
It shows common cases, such as getting a list of items, update an item,
dealing with client errors an so on.

## Usage

```python
import asyncio
import logging

from apiwrappers import make_driver

from example.client import GitHub
from example.middleware import ErrorMiddleware, LoggingMiddleware

logger = logging.getLogger(__name__)

# Set logging default level to INFO
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

# Create new drivers with `ErrorMiddleware` and `LoggingMiddleware`:
#   - `ErrorMiddleware` raises `GitHubException` for every response with
#     status code 400 and above.
#   - `LoggingMiddleware` logs every step of request/response cycle.
driver = make_driver("requests", ErrorMiddleware, LoggingMiddleware)
async_driver = make_driver("aiohttp", ErrorMiddleware, LoggingMiddleware)

# Credential pair to use for basic auth
creds = ("username", "password_or_token")

# Create a regular and asynchronous GitHub clients
github = GitHub("https://api.github.com", driver=driver, auth=creds)
async_github = GitHub("https://api.github.com", driver=async_driver, auth=creds)

# Make a regular requests
logger.info("Make a regular request")
user = github.user("unmade")  # UserDetail(id=9870176, ...
logger.info("User %s\n", user)

# Make an async request
logger.info("Make an async request")
user = asyncio.run(async_github.user("unmade"))  # UserDetail(id=9870176, ...
logger.info("User %s", user)
```
