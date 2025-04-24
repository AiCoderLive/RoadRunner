"""
Moduł odpowiedzialny za trenowanie modelu LSTM do predykcji czasów odpowiedzi.
Służy również jako punkt wejścia dla kontenera Docker.
"""
import os
import time
import pandas as pd
import numpy as np
from src.prediction_models.lstm.LstmResponsePredictor import LstmResponsePredictor
from src.utils.Paths import get_results_csv_file

def wait_for_results_file(file_path, max_retries=30, retry_interval=10):
    """Oczekuje na pojawienie się pliku wyników."""
    print(f"Oczekiwanie na plik wyników: {file_path}")
    retries = 0
    while retries < max_retries:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            print(f"Znaleziono plik wyników: {file_path}")
            return True
        print(f"Plik wyników jeszcze nie istnieje lub jest pusty. Próba {retries+1}/{max_retries}")
        time.sleep(retry_interval)
        retries += 1

    print(f"Nie znaleziono pliku wyników po {max_retries} próbach.")
    return False

def load_and_preprocess_data(file_path):
    """
    Wczytuje dane z pliku CSV i przygotowuje je do trenowania modelu LSTM.
    """
    try:
        print(f"Wczytywanie danych z: {file_path}")
        data = pd.read_csv(file_path)

        # Konwersja czasu
        data['StartTime'] = pd.to_datetime(data['StartTime'], format='%H:%M:%S:%f')
        data['EndTime'] = pd.to_datetime(data['EndTime'], format='%H:%M:%S:%f')

        # Przygotowanie danych do modelu
        vusers_data = data['VusersNumber'].values.reshape(-1, 1)
        response_times = data['ResponseTime[ms]'].values.reshape(-1, 1)

        print(f"Załadowano {len(data)} rekordów.")
        return vusers_data, response_times
    except Exception as e:
        print(f"Błąd podczas wczytywania danych: {e}")
        return None, None

def train_lstm_model(vusers_data, response_times, sequence_length=10, epochs=50, batch_size=32):
    """
    Trenuje model LSTM na podstawie przygotowanych danych.

    Args:
        vusers_data: Dane o liczbie użytkowników w formacie numpy array
        response_times: Dane o czasach odpowiedzi w formacie numpy array
        sequence_length: Długość sekwencji dla modelu LSTM
        epochs: Liczba epok trenowania
        batch_size: Rozmiar batcha

    Returns:
        bool: True jeśli trenowanie zakończyło się sukcesem, False w przeciwnym przypadku
    """
    print("Rozpoczynam trenowanie modelu LSTM...")

    # Tworzenie nowego modelu
    predictor = LstmResponsePredictor(sequence_length=sequence_length)

    # Trenowanie modelu
    success = predictor.train(vusers_data, response_times, epochs=epochs, batch_size=batch_size)

    if success:
        # Zapisanie modelu
        model_dir = os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, "lstm_predictor.h5")
        predictor.save_model(model_path)
        print(f"Model został zapisany do: {model_path}")

        # Ocena modelu i zapisanie predykcji
        results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "results")
        os.makedirs(results_dir, exist_ok=True)
        predictions_path = os.path.join(results_dir, "predictions.csv")

        # Zapisanie predykcji do pliku CSV bez uruchamiania wizualizacji
        predictor.evaluate_predictions(
            vusers_data,
            response_times,
            save_csv=True,
            visualize=False,
            output_path=predictions_path
        )

        print(f"Predykcje zapisane do: {predictions_path}")
        return True
    else:
        print("Trenowanie modelu nie powiodło się.")
        return False

def predict_response_time(vusers_sequence, model_path=None):
    """
    Wykonuje predykcję czasu odpowiedzi na podstawie sekwencji liczby użytkowników.

    Args:
        vusers_sequence: Sekwencja liczby użytkowników
        model_path: Ścieżka do zapisanego modelu (opcjonalnie)

    Returns:
        float: Przewidywany czas odpowiedzi
    """
    if model_path is None:
        model_dir = os.path.join(os.path.dirname(__file__), "models")
        model_path = os.path.join(model_dir, "lstm_predictor.h5")

    if not os.path.exists(model_path):
        print(f"Nie znaleziono modelu w ścieżce: {model_path}")
        return None

    # Załadowanie modelu
    predictor = LstmResponsePredictor(model_path=model_path)

    # Predykcja
    return predictor.predict_response_time(vusers_sequence)

def calculate_optimal_vusers(target_response_time, current_vusers, model_path=None, max_increase=50):
    """
    Oblicza optymalną liczbę użytkowników dla docelowego czasu odpowiedzi.

    Args:
        target_response_time: Docelowy czas odpowiedzi w milisekundach
        current_vusers: Aktualna liczba użytkowników
        model_path: Ścieżka do zapisanego modelu (opcjonalnie)
        max_increase: Maksymalny wzrost liczby użytkowników do sprawdzenia

    Returns:
        int: Optymalna liczba użytkowników
    """
    if model_path is None:
        model_dir = os.path.join(os.path.dirname(__file__), "models")
        model_path = os.path.join(model_dir, "lstm_predictor.h5")

    if not os.path.exists(model_path):
        print(f"Nie znaleziono modelu w ścieżce: {model_path}")
        return None

    # Załadowanie modelu
    predictor = LstmResponsePredictor(model_path=model_path)

    # Obliczenie optymalnej liczby użytkowników
    return predictor.predict_optimal_vusers(target_response_time, current_vusers, max_increase)

def main():
    """
    Główna funkcja skryptu uruchomieniowego.
    """
    print("Uruchamiam trenowanie modelu LSTM...")

    # Ścieżka do pliku z wynikami testów
    results_file = get_results_csv_file()

    # Oczekiwanie na plik wyników
    if not wait_for_results_file(results_file):
        print("Nie można kontynuować bez pliku wyników.")
        return

    # Wczytanie i przetworzenie danych
    vusers_data, response_times = load_and_preprocess_data(results_file)

    if vusers_data is None or response_times is None:
        print("Nie udało się wczytać danych.")
        return

    # Sprawdzenie, czy mamy wystarczającą ilość danych
    if len(vusers_data) < 50:  # Minimalny próg danych
        print(f"Za mało danych do trenowania modelu ({len(vusers_data)} rekordów). Potrzeba co najmniej 50.")
        return

    # Trenowanie modelu
    success = train_lstm_model(
        vusers_data,
        response_times,
        sequence_length=10,  # Długość sekwencji dla modelu LSTM
        epochs=50,           # Liczba epok trenowania
        batch_size=32        # Rozmiar batcha
    )

    if success:
        print("Proces trenowania i ewaluacji modelu LSTM zakończony pomyślnie.")
    else:
        print("Proces trenowania i ewaluacji modelu LSTM zakończony niepowodzeniem.")

if __name__ == "__main__":
    main()