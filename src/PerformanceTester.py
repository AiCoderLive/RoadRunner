import requests
import threading
import time
from datetime import datetime
import csv


class PerformanceTester:
    def __init__(self, url, method="GET"):
        self.url = url
        self.method = method.upper()
        self.results = []

    def send_request(self, user_id, data=None, headers=None):
        start_time = datetime.now().strftime('%H:%M:%S')
        if hasattr(requests, self.method.lower()):
            request_method = getattr(requests, self.method.lower())
            response = request_method(self.url, data=data, headers=headers)
        else:
            print(f"HTTP method {self.method} is not supported.")
            return
        end_time = datetime.now().strftime('%H:%M:%S')
        response_time = round(response.elapsed.total_seconds() * 1000, 2)

        print(
            f"User {user_id}: Request sent at {start_time}, Response received at {end_time}, Response time: {response_time}ms")
        self.results.append({
            'StartTime': start_time,
            'EndTime': end_time,
            'ResponseTime': response_time
        })

    def run_scenario(self, scenario, use_interval=False, request_interval=0, data=None, headers=None):
        for users, duration in scenario:
            threads = []
            start_time = time.time()
            while time.time() - start_time < duration:
                for i in range(users):
                    t = threading.Thread(target=self.send_request, args=(i, data, headers))
                    t.start()
                    threads.append(t)
                    if use_interval and request_interval > 0:
                        time.sleep(request_interval)
                if not use_interval:
                    time.sleep(1)  # Default behavior without interval
            for t in threads:
                t.join()

    def save_results(self, filename='results.csv'):
        with open(filename, mode='a', newline='') as file:  # Change mode to 'a' for appending
            fieldnames = ['StartTime', 'EndTime', 'ResponseTime']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:  # Write header only if file is empty
                writer.writeheader()
            for result in self.results:
                writer.writerow(result)
            self.results = []  # Clear results after writing
