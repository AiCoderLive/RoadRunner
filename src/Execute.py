import argparse
import csv

from src.utils.Scenario import Scenario
from src.utils.Request import Request

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Execute scenarios.')
parser.add_argument('--max_timeout', type=int, default=1, help='Maximum timeout for server response in seconds.')
args = parser.parse_args()

# Initialize and prepare CSV file for results
with open(Scenario.results_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["VusersNumber", "URL", "StartTime", "EndTime", "ResponseTime[ms]"])

# Define scenarios
request1 = (Request("First URL").set_url("https://www.wp.pl/").set_method("GET").set_headers(""))
Scenario.requests.append(request1)

# Set interval between requests
scenario = Scenario(max_timeout=args.max_timeout)
scenario.speed(1, 300).set_interval(10)
# Scenario.speed(5, 300).set_interval(0.1)
# Scenario.speed(10, 300).set_interval(0.1)

# Scenario.once() # Execute all scenarios sequentially, once each

