from apiwrappers import Method, Request


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
