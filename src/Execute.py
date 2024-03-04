import requests
import threading
import time
import csv
from datetime import datetime


# Definicja klasy Scenario
# Modyfikacja klasy Scenario, aby umożliwić zapisywanie i przekazywanie zmiennych między scenariuszami
class Scenario:
    shared_variables = {}  # Słownik na zmienne współdzielone między scenariuszami

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
        self.body = body.format(**Scenario.shared_variables)  # Użycie zmiennych współdzielonych
        return self

    def save(self, key):
        response = self.send_request()
        Scenario.shared_variables[key] = response.json().get(key)  # Zapis do słownika współdzielonych zmiennych
        return self

    def printResponse(self):
        response = self.send_request()
        print(response.text)
        return response

    def send_request(self):
        # Logika wysyłania żądania analogiczna jak poprzednio
        if self.method == "GET":
            return requests.get(self.url, headers=self.headers)
        elif self.method == "POST":
            return requests.post(self.url, headers=self.headers, data=self.body)
        elif self.method == "PUT":
            return requests.put(self.url, headers=self.headers, data=self.body)


# Klasa do zarządzania wydajnością
class Speed:
    scenarios = []
    results_file = 'results.csv'

    @staticmethod
    def run_scenario(scenario, vusers, duration):
        start_time = time.time()
        while time.time() - start_time < duration:
            response = scenario.printResponse()
            Speed.log_result(vusers, scenario.url, response)

    @staticmethod
    def run(vusers, duration):
        threads = []
        for _ in range(vusers):
            for scenario in Speed.scenarios:
                thread = threading.Thread(target=Speed.run_scenario, args=(scenario, vusers, duration))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

    @staticmethod
    def log_result(vusers, url, response):
        end_time = datetime.now()
        start_time = end_time - response.elapsed
        with open(Speed.results_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(
                [vusers, url, start_time.strftime('%H:%M:%S:%f')[:-3], end_time.strftime('%H:%M:%S:%f')[:-3],
                 response.elapsed.total_seconds() * 1000])


# Przygotowanie pliku results.csv
with open('results.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["VuserNumber", "URL", "StartTime", "EndTime", "ResponseTime[ms]"])

# Definicja scenariuszy
scenario1 = Scenario("First URL").set_url("http://httpbin.org/get").set_method("GET").set_headers("").save("X-Amzn-Trace-Id")
scenario2 = Scenario("Second URL").set_url("http://httpbin.org/post").set_method("POST").set_headers("").set_body("X-Amzn-Trace-Id: {X-Amzn-Trace-Id}")
scenario3 = Scenario("Third URL").set_url("http://httpbin.org/put").set_method("PUT").set_headers("")

# Dodanie scenariuszy do listy
Speed.scenarios.append(scenario1)
Speed.scenarios.append(scenario2)
Speed.scenarios.append(scenario3)

# Uruchomienie testów
Speed.run(1, 10)  # 1 użytkownik przez 10 sekund
Speed.run(2, 20)  # 2 użytkowników
Speed.run(10, 20)  # 2 użytkowników
