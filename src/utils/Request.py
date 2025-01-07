import time
import requests
from requests.exceptions import ConnectionError, Timeout

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

    def print_response(self, timeout=None):
        if timeout is None or timeout <= 0:
            timeout = 10  # Set a default timeout if the provided value is invalid
        response = self.send_request(timeout=timeout)
        print(response.text)
        return response

    def send_request(self, timeout=10, max_retries=5, backoff_factor=0.3):
        if timeout <= 0:
            timeout = 10  # Ensure timeout is greater than 0
        retries = 0
        while retries < max_retries:
            try:
                if self.method == "GET":
                    response = requests.get(self.url, headers=self.headers, timeout=timeout)
                elif self.method == "POST":
                    response = requests.post(self.url, headers=self.headers, data=self.body, timeout=timeout)
                elif self.method == "PUT":
                    response = requests.put(self.url, headers=self.headers, data=self.body, timeout=timeout)
                response.raise_for_status()  # Raise an exception for HTTP errors
                return response
            except (ConnectionError, Timeout) as e:
                retries += 1
                wait = backoff_factor * (2 ** retries)
                print(f"Retrying in {wait} seconds...")
                time.sleep(wait)
        raise ConnectionError(f"Failed to connect to {self.url} after {max_retries} retries")