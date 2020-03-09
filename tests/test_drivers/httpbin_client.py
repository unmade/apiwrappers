from apiwrappers import Method, Request, Url
from apiwrappers.auth import TokenAuth


class HttpBin:
    def __init__(self, host, driver):
        self.url = Url(host)
        self.driver = driver

    def get(self, params=None):
        """The request's query parameters."""
        request = Request(Method.GET, self.url("/get"), query_params=params)
        return self.driver.fetch(request)

    def post(self, data=None, files=None, json=None):
        """The request's POST parameters."""
        request = Request(
            Method.POST, self.url("/post"), data=data, files=files, json=json
        )
        return self.driver.fetch(request)

    def headers(self, headers):
        """Return the incoming request's HTTP headers."""
        request = Request(Method.GET, self.url("/headers"), headers=headers)
        return self.driver.fetch(request)

    def response_headers(self, headers):
        """Returns a set of response headers from the query string."""
        request = Request(
            Method.GET, self.url("/response-headers"), query_params=headers
        )
        return self.driver.fetch(request)

    def cookies(self, cookies):
        """Returns cookie data."""
        request = Request(Method.GET, self.url("/cookies"), cookies=cookies)
        return self.driver.fetch(request)

    def set_cookie(self, name, value):
        """Sets a cookie and redirects to cookie list."""
        url = self.url("/cookies/set/{name}/{value}", name=name, value=value)
        request = Request(Method.GET, url)
        return self.driver.fetch(request)

    def delay(self, delay, timeout):
        """Returns a delayed response (max of 10 seconds)."""
        request = Request(Method.GET, self.url("/delay/{delay}", delay=delay))
        return self.driver.fetch(request, timeout=timeout)

    def html(self):
        """Returns a simple HTML document."""
        request = Request(Method.GET, self.url("/html"))
        return self.driver.fetch(request)

    def basic_auth(self, login, password):
        """Prompts the user for authorization using HTTP Basic Auth."""
        url = self.url("/basic-auth/{user}/{passwd}", user=login, passwd=password)
        request = Request(Method.GET, url, auth=(login, password))
        return self.driver.fetch(request)

    def bearer_auth(self, token):
        """Prompts the user for authorization using bearer authentication."""
        request = Request(Method.GET, self.url("/bearer"), auth=TokenAuth(token))
        return self.driver.fetch(request)

    def complex_auth_flow(self):
        """Gets a UUID4 and uses it for bearer authentication."""

        def auth_flow():
            response = yield Request(Method.GET, self.url("/uuid"))
            return TokenAuth(response.json()["uuid"])()

        request = Request(Method.GET, self.url("/bearer"), auth=auth_flow)
        return self.driver.fetch(request)
