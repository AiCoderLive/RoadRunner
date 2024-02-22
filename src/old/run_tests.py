import subprocess
import threading
from PerformanceTester import  PerformanceTester # Zakładamy, że klasa PerformanceTester jest zapisana w pliku performance_tester.py

# Definicja scenariusza testowego
scenario = [(1, 5),
            (2, 5)]  # Przykładowy scenariusz: 1 użytkownik przez 5 sekund, potem 2 użytkownicy przez kolejne 5 sekund


def start_dash_monitoring():
    subprocess.run(["python", "monitoring.py"])


def run_performance_test():
    url = "http://httpbin.org/get"
    tester = PerformanceTester(url)
    tester.run_scenario(scenario)
    tester.save_results()


if __name__ == "__main__":
    # Uruchomienie monitoringu w tle
    monitoring_thread = threading.Thread(target=start_dash_monitoring)
    monitoring_thread.start()

    # Uruchomienie testu wydajnościowego
    run_performance_test()
