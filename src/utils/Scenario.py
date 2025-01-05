import csv
import datetime
import threading
import time

from src.utils.Paths import get_results_csv_file


class Scenario:
    results_file = get_results_csv_file()
    requests = []
    threads = []
    lock = threading.Lock()  # Initialize the lock

    def __init__(self, interval=0, max_timeout=0):
        self.interval = interval
        self.max_timeout = max_timeout

    def set_interval(self, interval):
        self.interval = interval
        return self

    def speed(self, users, duration):
        for request in Scenario.requests:
            for _ in range(users):
                thread = threading.Thread(target=self.run_scenario, args=(request, users, duration))
                Scenario.threads.append(thread)
                thread.start()

        for thread in Scenario.threads:
            thread.join()
        return self

    def run_scenario(self, request, vusers, duration):
        start_time = time.time()
        while time.time() - start_time < duration:
            response = request.print_response(timeout=self.max_timeout)
            Scenario.log_result(vusers, request.url, response)
            time.sleep(self.interval)  # Use the interval between requests

    @staticmethod
    def log_result(vusers, url, response):
        end_time = datetime.datetime.now()
        try:
            start_time = end_time - response.elapsed
            response_time = round(response.elapsed.total_seconds() * 1000, 3)  # Round the response time
            with Scenario.lock:  # Lock the block of code to ensure thread safety
                with open(Scenario.results_file, mode='a', newline='') as file:
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
        for request in Scenario.requests:
            response = request.print_response()
            # Logging with a vuser number of 1 as it's a single execution
            Scenario.log_result(1, request.url, response)