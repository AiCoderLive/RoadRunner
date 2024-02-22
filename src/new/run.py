# Utworzenie instancji klasy PerformanceTester dla URL 'http://httpbin.org/get' i metody GET
from PerformanceTester import PerformanceTester

tester = PerformanceTester(url='http://httpbin.org/get', method='GET')

# Definicja scenariusza testowego
scenario = [
    (1, 10),  # 1 użytkownik przez 10 sekund
    (2, 10),  # 2 użytkowników przez kolejne 10 sekund
    (3, 10)   # 3 użytkowników przez kolejne 10 sekund
]

# Uruchomienie scenariusza testowego
tester.run_scenario(scenario)

# Zapisanie wyników testu do pliku CSV
tester.save_results('test_results.csv')
