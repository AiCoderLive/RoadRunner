import threading
import app  # Import aplikacji Dash
from src.PerformanceTester import PerformanceTester


def run_test(url, scenario):
    tester = PerformanceTester(url)
    tester.run_scenario(scenario)
    tester.save_results()


def run_dash_app():
    app.app.run_server(debug=False)  # Uruchomienie serwera Dash


if __name__ == "__main__":
    url = "http://httpbin.org/get"
    scenario = [(1, 10), (2, 10), (3, 10)]  # Przykładowy scenariusz

    # Uruchomienie aplikacji Dash w oddzielnym wątku
    dash_thread = threading.Thread(target=run_dash_app)
    dash_thread.start()

    # Uruchomienie testu w głównym wątku
    run_test(url, scenario)

    # Oczekiwanie na zakończenie wątku Dash (opcjonalnie, w zależności od potrzeb)
    dash_thread.join()
