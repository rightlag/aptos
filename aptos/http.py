import urllib.request


class HTTPRequestInitializer:
    def __call__(self, request):
        request.add_header('accept', 'application/json')
        request.add_header('content-type', 'application/json')


class HTTPRequestFactory:
    def __init__(self, initializer=None):
        self.initializer = initializer

    def build_request(self, method, url, body=None):
        request = urllib.request.Request(url, data=body, method=method)
        if self.initializer is not None:
            self.initializer(request)
        return urllib.request.urlopen(request)  # synchronous
