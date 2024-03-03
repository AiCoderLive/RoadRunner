import requests
import time
import csv
from datetime import datetime


class Scenario:
    def __init__(self, name):
        self.name = name
        self.url = ""
        self.method = ""
        self.headers = {}
        self.body = ""

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


class Speed:
    scenarios = []

    @classmethod
    def add_scenario(cls, scenario):
        cls.scenarios.append(scenario)

    @classmethod
    def run(cls, user_count, duration):
        start_time = time.time()
        with open('results.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["VuserNumber", "StartTime", "EndTime", "ResponseTime[ms]"])

        while time.time() - start_time < duration:
            for user in range(user_count):
                for scenario in cls.scenarios:
                    start_request_time = datetime.now()
                    if scenario.method == "GET":
                        response = requests.get(scenario.url, headers=scenario.headers)
                    elif scenario.method == "POST":
                        response = requests.post(scenario.url, headers=scenario.headers, data=scenario.body)
                    elif scenario.method == "PUT":
                        response = requests.put(scenario.url, headers=scenario.headers, data=scenario.body)

                    end_request_time = datetime.now()
                    print(user + 1, scenario.url, response.status_code,
                          (end_request_time - start_request_time).total_seconds() * 1000)
                    with open('results.csv', mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([user + 1, start_request_time.strftime("%H:%M:%S:%f")[:-3],
                                         end_request_time.strftime("%H:%M:%S:%f")[:-3],
                                         (end_request_time - start_request_time).total_seconds() * 1000])


# Przykład użycia
Speed.add_scenario(
    Scenario("First URL").set_url("http://httpbin.org/get").set_method("GET").set_headers("").set_body(""))
Speed.add_scenario(
    Scenario("Second URL").set_url("http://httpbin.org/post").set_method("POST").set_headers("").set_body(""))
Speed.add_scenario(
    Scenario("Third URL").set_url("http://httpbin.org/put").set_method("PUT").set_headers("").set_body(""))
Speed.run(1, 10)  # Uruchomienie dla 1 użytkownika przez 10 sekund
Speed.run(2, 20)  # Uruchomienie dla 2 użytkowników przez 20 sekund
Speed.run(3, 20)
