import csv

from src.utils.Scenario import Scenario
from src.utils.Request import Request

# Initialize and prepare CSV file for results
with open(Scenario.results_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["VusersNumber", "URL", "StartTime", "EndTime", "ResponseTime[ms]"])

# Definicja scenariuszy
request1 = (Request("First URL").set_url("https://www.wp.pl/").set_method("GET").set_headers(""))
Scenario.requests.append(request1)

# Execute tests
Scenario.speed(1, 5)

# Scenario.once() # Execute all scenarios sequentially, once each

