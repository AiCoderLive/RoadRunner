import csv
import requests
from datetime import datetime


class RoadRunner:
    def __init__(self, url, scenario):
        self.url = url
        self.scenario = scenario
        self.results = []

    def run(self):
        for user_count, duration in self.scenario:
            for i in range(duration):
                start_time = datetime.now()  # Get start time as datetime
                response = requests.get(self.url)
                end_time = datetime.now()  # Get end time as datetime
                response_time = (end_time - start_time).total_seconds() * 1000  # Calculate response time in ms

                # Format start and end time
                start_time_str = start_time.strftime("%H:%M:%S:%f")[:-3]
                end_time_str = end_time.strftime("%H:%M:%S:%f")[:-3]

                self.results.append((start_time_str, end_time_str, response_time))  # Store results
                self.print_request(start_time_str, user_count, response_time)

    def save_results(self):
        with open("results.csv", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["StartTime", "EndTime", "ResponseTime"])
            for start_time_str, end_time_str, response_time in self.results:
                writer.writerow([start_time_str, end_time_str, f"{response_time:.3f}"])

    def print_request(self, start_time_str, user_count, response_time):
        print(f"[{start_time_str}] {user_count} users: {response_time:.3f}ms")


if __name__ == "__main__":
    url = "http://httpbin.org"
    scenario = [(1, 10), (2, 10), (3, 10)]

    tester = RoadRunner(url, scenario)
    tester.run()
    tester.save_results()
