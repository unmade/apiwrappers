from apiwrappers import Method, Request, Url
from apiwrappers.auth import TokenAuth


class APIWrapper:
    def __init__(self, host, driver):
        self.url = Url(host)
        self.driver = driver

    def get_hello_world(self):
        request = Request(Method.GET, self.url)
        return self.driver.fetch(request)

    def echo_headers(self, headers):
        request = Request(Method.POST, self.url, headers=headers)
        return self.driver.fetch(request)

    def echo_query_params(self, query_params):
        request = Request(Method.GET, self.url, query_params=query_params)
        return self.driver.fetch(request)

    def echo_cookies(self, cookies):
        request = Request(Method.GET, self.url, cookies=cookies)
        return self.driver.fetch(request)

    def send_data(self, payload):
        request = Request(Method.POST, self.url, data=payload)
        return self.driver.fetch(request)

    def send_files(self, payload):
        request = Request(Method.POST, self.url, files=payload)
        return self.driver.fetch(request)

    def send_json(self, payload):
        request = Request(Method.POST, self.url, json=payload)
        return self.driver.fetch(request)

    def timeout(self, timeout):
        request = Request(Method.GET, self.url)
        return self.driver.fetch(request, timeout=timeout)

    def verify(self):
        request = Request(Method.GET, self.url)
        return self.driver.fetch(request)

    def cert(self):
        request = Request(Method.GET, self.url)
        return self.driver.fetch(request)

    def exception(self):
        request = Request(Method.GET, self.url)
        return self.driver.fetch(request)

    def middleware(self):
        request = Request(Method.GET, self.url)
        return self.driver.fetch(request)

    def basic_auth(self):
        request = Request(Method.GET, self.url, auth=("user", "passwd"))
        return self.driver.fetch(request)

    def token_auth(self):
        request = Request(Method.GET, self.url, auth=TokenAuth("authtoken"))
        return self.driver.fetch(request)

    def complex_auth_flow(self):
        def auth_flow():
            response = yield Request(Method.POST, self.url("/auth"))
            return TokenAuth(response.json()["token"])()

        request = Request(Method.GET, self.url, auth=auth_flow)
        return self.driver.fetch(request)
