import requests
import threading
import time
import csv
from datetime import datetime, timedelta
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

class Scenario:
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
        self.body = body.format(**Scenario.shared_variables)  # Use shared variables
        return self

    def save(self, key):
        response = self.send_request()
        Scenario.shared_variables[key] = response.json().get(key)  # Save to shared variables dictionary
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


class Run:
    scenarios = []
    results_file = 'results.csv'
    lock = threading.Lock()  # Add a lock for thread-safe file writing

    @staticmethod
    def speed(vusers, duration):
        threads = []
        for _ in range(vusers):
            for scenario in Run.scenarios:
                thread = threading.Thread(target=Run.run_scenario, args=(scenario, vusers, duration))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

    @staticmethod
    def run_scenario(scenario, vusers, duration):
        start_time = time.time()
        while time.time() - start_time < duration:
            response = scenario.print_response()
            Run.log_result(vusers, scenario.url, response)

    @staticmethod
    def log_result(vusers, url, response):
        end_time = datetime.now()
        try:
            start_time = end_time - response.elapsed
            response_time = round(response.elapsed.total_seconds() * 1000, 3)  # Round the response time
            with Run.lock:  # Lock the block of code to ensure thread safety
                with open(Run.results_file, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(
                        [vusers, url, start_time.strftime('%H:%M:%S:%f')[:-3],
                         end_time.strftime('%H:%M:%S:%f')[:-3],
                         response_time])  # Use the rounded response time
        except Exception as e:
            print(f"Error logging result: {e}")

    # Execute all scenarios sequentially, once each
    @staticmethod
    def once():
        for scenario in Run.scenarios:
            response = scenario.print_response()
            # Logging with a vuser number of 1 as it's a single execution
            Run.log_result(1, scenario.url, response)


# Initialize and prepare CSV file for results
with open(Run.results_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["VusersNumber", "URL", "StartTime", "EndTime", "ResponseTime[ms]"])

# Definicja scenariuszy
scenario1 = Scenario("First URL").set_url("http://httpbin.org/get").set_method("GET").set_headers("").save(
    "X-Amzn-Trace-Id")
scenario2 = Scenario("Second URL").set_url("http://httpbin.org/post").set_method("POST").set_headers("").set_body(
    "X-Amzn-Trace-Id: {X-Amzn-Trace-Id}")
scenario3 = Scenario("Third URL").set_url("http://httpbin.org/put").set_method("PUT").set_headers("")

Run.scenarios.append(scenario1)
Run.scenarios.append(scenario2)
Run.scenarios.append(scenario3)

# Execute tests
Run.speed(1, 10)  # 1 user for 10 seconds
Run.speed(2, 20)  # 2 users for 20 seconds
# Run.speed(10, 20)  # 10 users for 20 seconds
# Run.speed(20, 20)  # 5 users for 20 seconds

# Run.once() # Execute all scenarios sequentially, once each

# ARIMA Model Implementation

# Load data
data = pd.read_csv('results.csv')

# Preprocess data
data['EndTime'] = pd.to_datetime(data['EndTime'], format='%H:%M:%S:%f')
data['ResponseTime[ms]'] = data['ResponseTime[ms]'].astype(float)

# Train ARIMA model on ResponseTime
response_times = data['ResponseTime[ms]']
model = ARIMA(response_times, order=(5, 1, 0))
model_fit = model.fit()

# Make predictions for the next 20 seconds
predictions = model_fit.forecast(steps=20)

# Generate predicted EndTime
last_end_time = data['EndTime'].iloc[-1]
predicted_end_times = [last_end_time + timedelta(seconds=i) for i in range(1, 21)]

# Save predictions to predicted_results.csv
predicted_data = pd.DataFrame({
    'EndTime': predicted_end_times,
    'ResponseTime[ms]': predictions
})
predicted_data.to_csv('predicted_results.csv', index=False)