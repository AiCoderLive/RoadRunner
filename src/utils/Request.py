import requests


class Request:
    shared_variables = {}  # Shared variables dictionary

    def __init__(self, name):
        self.name = name
        self.url = None
        self.method = None
        self.headers = {}
        self.body = None

    def set_url(self, url):
        self.url = url
        return self

    def set_method(self, method):
        self.method = method.upper()
        return self

    def set_headers(self, headers):
        self.headers = headers
        return self

    def set_body(self, body):
        self.body = body.format(**Request.shared_variables)  # Use shared variables
        return self

    def save(self, key):
        response = self.send_request()
        Request.shared_variables[key] = response.json().get(key)  # Save to shared variables dictionary
        return self

    def print_response(self):
        response = self.send_request()
        print(response.text)
        return response

    def send_request(self):
        if self.method == "GET":
            return requests.get(self.url, headers=self.headers)
        elif self.method == "POST":
            return requests.post(self.url, headers=self.headers, data=self.body)
        elif self.method == "PUT":
            return requests.put(self.url, headers=self.headers, data=self.body)