from apiwrappers import Method, Request
from apiwrappers.auth import TokenAuth


class APIWrapper:
    def __init__(self, host, driver):
        self.host = host
        self.driver = driver

    def get_hello_world(self):
        request = Request(Method.GET, self.host, "/")
        return self.driver.fetch(request)

    def echo_headers(self, headers):
        request = Request(Method.POST, self.host, "/", headers=headers)
        return self.driver.fetch(request)

    def echo_query_params(self, query_params):
        request = Request(Method.GET, self.host, "/", query_params=query_params)
        return self.driver.fetch(request)

    def echo_cookies(self, cookies):
        request = Request(Method.GET, self.host, "/", cookies=cookies)
        return self.driver.fetch(request)

    def send_data(self, payload):
        request = Request(Method.POST, self.host, "/", data=payload)
        return self.driver.fetch(request)

    def send_json(self, payload):
        request = Request(Method.POST, self.host, "/", json=payload)
        return self.driver.fetch(request)

    def timeout(self, timeout):
        request = Request(Method.GET, self.host, "/")
        return self.driver.fetch(request, timeout=timeout)

    def verify_ssl(self, verify_ssl):
        request = Request(Method.GET, self.host, "/")
        return self.driver.fetch(request, verify_ssl=verify_ssl)

    def exception(self):
        request = Request(Method.GET, self.host, "/")
        return self.driver.fetch(request)

    def middleware(self):
        request = Request(Method.GET, self.host, "/")
        return self.driver.fetch(request)

    def basic_auth(self):
        request = Request(Method.GET, self.host, "/", auth=("user", "passwd"))
        return self.driver.fetch(request)

    def token_auth(self):
        request = Request(Method.GET, self.host, "/", auth=TokenAuth("authtoken"))
        return self.driver.fetch(request)
