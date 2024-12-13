import csv
import datetime
import threading
import time

class Scenario:
    results_file = 'results.csv'
    requests = []
    threads = []
    lock = threading.Lock()  # Initialize the lock

    @staticmethod
    def speed(users, duration):
        for request in Scenario.requests:
            for _ in range(users):
                thread = threading.Thread(target=Scenario.run_scenario, args=(request, users, duration))
                Scenario.threads.append(thread)
                thread.start()

        for thread in Scenario.threads:
            thread.join()

    @staticmethod
    def run_scenario(request, vusers, duration):
        start_time = time.time()
        while time.time() - start_time < duration:
            response = request.print_response()
            Scenario.log_result(vusers, request.url, response)

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