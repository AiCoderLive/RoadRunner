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
# request1 = (Request("First URL").set_url("https://www.wp.pl/").set_method("GET").set_headers(""))
request1 = (Request("First URL").set_url("http://192.168.56.103:5000/api/basic").set_method("GET").set_headers(""))
Scenario.requests.append(request1)


# Set interval between requests
scenario = Scenario()
scenario.speed(1, 60)
scenario.speed(20, 60)
scenario.speed(30, 60)
scenario.speed(40, 60)
scenario.speed(50, 60)
scenario.speed(60, 60)
scenario.speed(70, 60)
scenario.speed(80, 60)
scenario.speed(90, 60)
scenario.speed(100, 60)
scenario.speed(110, 60)
scenario.speed(120, 60)
scenario.speed(130, 60)
scenario.speed(140, 60)
scenario.speed(150, 60)
scenario.speed(160, 60)
scenario.speed(170, 60)

# Scenario.once() # Execute all scenarios sequentially, once each

