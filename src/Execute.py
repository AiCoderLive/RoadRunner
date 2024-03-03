import requests
import time
import threading
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
    def __init__(self):
        self.scenarios = []
        self.times = []

    def run(self, users, duration):
        self.times.append((users, duration))
        return self


def send_request(scenario, user_number):
    start_time = datetime.now()
    response = requests.request(method=scenario.method, url=scenario.url, headers=scenario.headers, data=scenario.body)
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() * 1000  # Konwersja na milisekundy

    print(f"User {user_number}: {scenario.url} - Status Code: {response.status_code}, Response Time: {duration}ms")
    return {
        'VuserNumber': user_number,
        'StartTime': start_time.strftime("%H:%M:%S:%f")[:-3],
        'EndTime': end_time.strftime("%H:%M:%S:%f")[:-3],
        'ResponseTime[ms]': f"{duration:.2f}"
    }


def execute_test(scenarios, times):
    with open('results.csv', 'w', newline='') as csvfile:
        fieldnames = ['VuserNumber', 'StartTime', 'EndTime', 'ResponseTime[ms]']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for users, duration in times:
            end_time = time.time() + duration
            threads = []
            while time.time() < end_time:
                for user_number in range(1, users + 1):
                    for scenario in scenarios:
                        thread = threading.Thread(target=lambda q, arg1, arg2: q.append(send_request(arg1, arg2)),
                                                  args=(results, scenario, user_number))
                        threads.append(thread)
                        thread.start()
                        time.sleep(0.5)  # Czekaj sekundę przed uruchomieniem kolejnego wątku

            for thread in threads:
                thread.join()  # Czekaj na zakończenie wszystkich wątków

            for result in results:
                writer.writerow(result)


scenarios = [
    Scenario("First URL").set_url("http://httpbin.org/get").set_method("GET"),
    Scenario("Second URL").set_url("http://httpbin.org/post").set_method("POST"),
    Scenario("Third URL").set_url("http://httpbin.org/put").set_method("PUT")
]

speed = Speed()
speed.run(1, 10).run(2, 20).run(3, 10)
results = []
execute_test(scenarios, speed.times)
