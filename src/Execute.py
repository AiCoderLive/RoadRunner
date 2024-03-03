import requests
import time
import csv
from datetime import datetime


class Scenario:
    def __init__(self, name):
        self.response = None
        self.name = name
        self.url = ""
        self.method = "GET"
        self.headers = {}
        self.body = None
        self.response_key = None

    def set_url(self, url):
        self.url = url
        return self

    def set_method(self, method):
        self.method = method
        return self

    def set_headers(self, headers):
        self.headers = headers
        return self

    def set_body(self, body):
        self.body = body
        return self

    def save(self, key):
        self.response_key = key
        return self

    def print_response(self):
        print(f"Response from {self.url}: {self.response}")
        return self

    def execute(self, user_id):
        start_time = datetime.now()
        if self.method == "GET":
            response = requests.get(self.url, headers=self.headers)
        elif self.method == "POST":
            response = requests.post(self.url, data=self.body, headers=self.headers)
        elif self.method == "PUT":
            response = requests.put(self.url, data=self.body, headers=self.headers)
        end_time = datetime.now()

        response_time = (end_time - start_time).total_seconds() * 1000
        print(f"URL: {self.url}, Status Code: {response.status_code}, Response Time: {response_time}ms")

        if self.response_key and self.response_key in response.json():
            global id
            id = response.json()[self.response_key]

        with open('results.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                [user_id, self.url, start_time.strftime('%H:%M:%S:%f')[:-3], end_time.strftime('%H:%M:%S:%f')[:-3],
                 format(response_time, '.2f')])

        self.response = response.text
        return self


class Speed:
    scenarios = []

    @staticmethod
    def run(user_id, duration):
        start_time = time.time()
        while time.time() - start_time < duration:
            for scenario in Speed.scenarios:
                scenario.execute(user_id)

    @staticmethod
    def add_scenario(scenario):
        Speed.scenarios.append(scenario)


# Clear or create the results.csv file
with open('results.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["VuserNumber", "URL", "StartTime", "EndTime", "ResponseTime[ms]"])

# Define scenarios
Speed.add_scenario(Scenario("First URL").set_url("http://httpbin.org/get").set_method("GET").save("X-Amzn-Trace-Id"))
Speed.add_scenario(
    Scenario("Second URL").set_url("http://httpbin.org/post").set_method("POST").set_headers("").set_body(
        "X-Amzn-Trace-Id: ${id}"))
Speed.add_scenario(Scenario("Third URL").set_url("http://httpbin.org/put").set_method("PUT").print_response())

# Execute scenarios
Speed.run(1, 10)  # 1 user for 10 seconds
Speed.run(2, 20)  # 2 users for 20 seconds
