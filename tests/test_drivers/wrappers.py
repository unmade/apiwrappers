from typing import Dict, Union

from apiwrappers import AsyncDriver, Driver, Method, Request


class APIWrapper:
    def __init__(self, host: str, driver: Union[Driver, AsyncDriver]):
        self.host = host
        self.driver = driver

    def get_hello_world(self):
        request = Request(Method.GET, self.host, "/",)
        return self.driver.fetch(request)

    def echo_headers(self, headers: Dict[str, str]):
        request = Request(Method.POST, self.host, "/", headers=headers)
        return self.driver.fetch(request)
