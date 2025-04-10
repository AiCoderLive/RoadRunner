#!/usr/bin/env python3
"""
Moduł predykcji LSTM wykorzystujący wszystkie dostępne dane z pliku results.csv.
"""

import os
import time
import pandas as pd
import numpy as np
from datetime import timedelta
from utils.Paths import get_results_csv_file
from prediction_models.lstm.CompleteDataPredictor import CompleteDataPredictor


def main():
    """
    Główna funkcja predykcji LSTM wykorzystująca wszystkie dostępne kolumny.
    """
    # Ścieżki do plików
    results_file = get_results_csv_file()
    model_path = 'model/complete_predictor.h5'
    encoders_path = 'model/encoders.pkl'
    predictions_file = os.path.join('src', 'results', 'predicted_results.csv')

    print(f"Complete LSTM Predictor - monitorowanie pliku: {results_file}")
    print(f"Model będzie zapisywany jako: {model_path}")
    print(f"Enkodery będą zapisywane jako: {encoders_path}")
    print(f"Predykcje będą zapisywane do: {predictions_file}")

    # Czekaj na dane
    while not os.path.exists(results_file) or os.path.getsize(results_file) < 100:
        print("Czekam na dane...")
        time.sleep(5)

    # Inicjalizacja predyktora
    predictor = CompleteDataPredictor(
        sequence_length=5,
        model_path=model_path if os.path.exists(model_path) else None,
        encoders_path=encoders_path if os.path.exists(encoders_path) else None
    )

    # Główna pętla predykcji
    last_size = 0
    last_train_time = 0
    while True:
        try:
            # Sprawdź, czy plik wyników został zaktualizowany
            current_size = os.path.getsize(results_file)
            current_time = time.time()

            # Jeśli są nowe dane, trenuj model i generuj predykcje
            if current_size > last_size or (current_time - last_train_time > 60):
                # Wczytaj dane
                data = pd.read_csv(results_file)

                # Sprawdź, czy mamy wystarczająco danych
                if len(data) < 10:
                    print("Za mało danych do treningu, czekam...")
                    time.sleep(5)
                    continue

                # Trenuj model
                print(f"Trenuję model na {len(data)} próbkach z wykorzystaniem wszystkich danych...")
                predictor.train(data, epochs=10, batch_size=32, validation_split=0.2)

                # Zapisz model
                predictor.save_model(model_path, encoders_path)

                # Generuj predykcje na następne 20 sekund
                print("Generuję predykcje...")
                predictions = []
                last_row = data.iloc[-1:].copy()
                last_end_time = pd.to_datetime(last_row['EndTime'].iloc[0], format='%H:%M:%S:%f')

                # Przygotuj dane do przewidywania następnych 20 sekund
                future_data_frames = []
                for i in range(20):
                    future_row = last_row.copy()
                    next_time = last_end_time + timedelta(seconds=i + 1)
                    future_row['EndTime'] = next_time.strftime('%H:%M:%S:%f')[:-3]
                    # Zakładamy, że StartTime jest 1ms wcześniej
                    future_row['StartTime'] = (next_time - timedelta(milliseconds=1)).strftime('%H:%M:%S:%f')[:-3]
                    future_data_frames.append(future_row)

                predicted_end_times = [last_end_time + timedelta(seconds=i + 1) for i in range(20)]

                # Generuj predykcje dla każdego przyszłego punktu czasowego
                for i in range(20):
                    # Przygotuj pełną sekwencję dla predykcji
                    if i == 0:
                        # Dla pierwszej predykcji użyj historycznych danych + pierwszej przyszłej wartości
                        seq_data = pd.concat([
                            data.iloc[-(predictor.sequence_length - 1):].copy(),
                            future_data_frames[0]
                        ]).reset_index(drop=True)
                    else:
                        # Dla kolejnych predykcji użyj części historycznych danych + dotychczasowych przyszłych wartości
                        hist_data = data.iloc[-(
                                    predictor.sequence_length - i - 1):].copy() if i < predictor.sequence_length - 1 else pd.DataFrame()
                        seq_data = pd.concat([
                            hist_data,
                            pd.concat(future_data_frames[:i + 1])
                        ]).reset_index(drop=True)

                        # Upewnij się, że mamy dokładnie sequence_length wierszy
                        if len(seq_data) > predictor.sequence_length:
                            seq_data = seq_data.iloc[-predictor.sequence_length:]

                    # Predykcja czasu odpowiedzi
                    pred_response = predictor.predict(seq_data)
                    predictions.append(pred_response)

                    # Aktualizacja przewidywanego czasu odpowiedzi dla wykorzystania w kolejnych predykcjach
                    future_data_frames[i]['ResponseTime[ms]'] = pred_response

                # Zapisz predykcje do pliku
                predicted_data = pd.DataFrame({
                    'EndTime': [t.strftime('%H:%M:%S:%f')[:-3] for t in predicted_end_times],
                    'ResponseTime[ms]': predictions
                })
                predicted_data.to_csv(predictions_file, index=False)
                print(f"Zapisano predykcje do {predictions_file}")

                # Aktualizuj ostatni czas treningu i rozmiar pliku
                last_size = current_size
                last_train_time = current_time

            # Poczekaj przed następnym sprawdzeniem
            time.sleep(5)

        except Exception as e:
            print(f"Błąd podczas generowania predykcji: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(10)


if __name__ == "__main__":
    main()