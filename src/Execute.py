import csv

from src.utils.Scenario import Scenario
from src.utils.Request import Request

# Initialize and prepare CSV file for results
with open(Scenario.results_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["VusersNumber", "URL", "StartTime", "EndTime", "ResponseTime[ms]"])

# Definicja scenariuszy
request1 = (Request("First URL").set_url("https://www.wp.pl/").set_method("GET").set_headers(""))
# request1 = (Request("First URL").set_url("http://192.168.56.103:5000/api/basic").set_method("GET").set_headers(""))
Scenario.requests.append(request1)

# Ustawienie różnicy między requestami na 100 ms

scenario = Scenario()
# duration are minutes
# Execute tests
scenario.speed(1,30).set_interval(1)
# Scenario.speed(5, 300).set_interval(0.1)
# Scenario.speed(10, 300).set_interval(0.1)

# Scenario.once() # Execute all scenarios sequentially, once each

