from src.new.PerformanceTester import PerformanceTester


class Run:
    def __init__(self, url):
        self.tester = PerformanceTester(url)

    def start_test(self, scenario):
        self.tester.run_scenario(scenario)
        self.tester.save_results()


# Przykład użycia
if __name__ == "__main__":
    url = "http://httpbin.org/get"
    scenario = [(1, 10), (2, 10), (0, 30),
                (3, 10)]  # Scenariusz: 1 użytkownik przez 10 sekund, potem 2 przez 10 sekund, potem 3 przez 10 sekund
    runner = Run(url)
    runner.start_test(scenario)
