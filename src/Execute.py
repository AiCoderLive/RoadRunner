import csv

from src.utils.Scenario import Scenario
from src.utils.Request import Request

# Initialize and prepare CSV file for results
with open(Scenario.results_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["VusersNumber", "URL", "StartTime", "EndTime", "ResponseTime[ms]"])

# Definicja scenariuszy
# scenario1 = (Scenario("First URL").set_url("http://httpbin.org/get").set_method("GET").set_headers(""))
request1 = (Request("First URL").set_url("https://www.wp.pl/").set_method("GET").set_headers(""))
# .save("X-Amzn-Trace-Id"))
# request2 = Scenario("Second URL").set_url("http://httpbin.org/post").set_method("POST").set_headers("").set_body(
#     "X-Amzn-Trace-Id: {X-Amzn-Trace-Id}")
# request3 = Scenario("Third URL").set_url("http://httpbin.org/put").set_method("PUT").set_headers("")

Scenario.requests.append(request1)
# Scenario.requests.append(request2)
# Scenario.requests.append(request3)

# Execute tests
Scenario.speed(1, 5)  # 1 user for 10 seconds
# Scenario.speed(2, 20)  # 2 users for 20 seconds
# Scenario.speed(5, 20)  # 10 users for 20 seconds
# Scenario.speed(20, 20)  # 5 users for 20 seconds

# Scenario.once() # Execute all scenarios sequentially, once each

