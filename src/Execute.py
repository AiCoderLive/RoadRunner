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
# request1 = (Request("First URL").set_url("http://192.168.56.103:5000/api/basic").set_method("GET").set_headers(""))
Scenario.requests.append(request1)


# Set interval between requests
scenario = Scenario()
scenario.speed(1, 120)
# scenario.speed(200, 120)
# scenario.speed(300, 120)
# scenario.speed(400, 120)
# scenario.speed(500, 120)
# scenario.speed(600, 120)
# scenario.speed(700, 120)
# scenario.speed(800, 120)
# scenario.speed(900, 120)
# scenario.speed(1000, 120)

# Scenario.once() # Execute all scenarios sequentially, once each

