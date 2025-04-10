import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input, Concatenate, Embedding, Flatten, Reshape
from tensorflow.keras.models import Model
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import pandas as pd
import pickle


class LstmPredictor:
    def __init__(self, sequence_length=5, model_path=None, encoders_path=None):
        """
        Inicjalizacja predyktora wykorzystującego wszystkie dostępne dane.

        Args:
            sequence_length: Długość sekwencji danych używanych do predykcji
            model_path: Ścieżka do zapisanego modelu
            encoders_path: Ścieżka do zapisanych enkoderów
        """
        self.sequence_length = sequence_length
        self.scaler_vusers = MinMaxScaler(feature_range=(0, 1))
        self.scaler_response = MinMaxScaler(feature_range=(0, 1))
        self.url_encoder = LabelEncoder()

        # Ładowanie modelu i enkoderów, jeśli istnieją
        if model_path and os.path.exists(model_path) and encoders_path and os.path.exists(encoders_path):
            self.model = load_model(model_path)
            self._load_encoders(encoders_path)
        else:
            self.model = None  # Model zostanie zbudowany po poznaniu wymiarów danych

        self.is_initialized = False
        self.embedding_dim = 8  # Wymiar embeddingu dla URL

    def _extract_time_features(self, time_column):
        """Ekstrahuje cechy czasowe z kolumny czasu."""
        # Konwertuje string czasu na datetime jeśli to konieczne
        if isinstance(time_column.iloc[0], str):
            time_column = pd.to_datetime(time_column, format='%H:%M:%S:%f')

        # Ekstrahuje cechy czasowe
        hour = time_column.dt.hour.values / 24.0  # Normalizacja do [0,1]
        minute = time_column.dt.minute.values / 60.0
        second = time_column.dt.second.values / 60.0
        microsecond = time_column.dt.microsecond.values / 1000000.0

        # Cechy cykliczne dla godziny
        hour_sin = np.sin(2 * np.pi * hour)
        hour_cos = np.cos(2 * np.pi * hour)

        # Przekształcenie do formatu macierzy
        time_features = np.column_stack([hour, minute, second, microsecond, hour_sin, hour_cos])
        return time_features

    def _build_model(self, n_urls):
        """Buduje model wykorzystujący wszystkie dostępne dane."""
        # Wejście dla liczby użytkowników
        vusers_input = Input(shape=(self.sequence_length, 1), name='vusers_input')

        # Wejście dla URL (zakodowane jako liczby całkowite)
        url_input = Input(shape=(self.sequence_length,), name='url_input', dtype='int32')

        # Wejście dla czasu rozpoczęcia
        start_time_input = Input(shape=(self.sequence_length, 6), name='start_time_input')

        # Wejście dla czasu zakończenia
        end_time_input = Input(shape=(self.sequence_length, 6), name='end_time_input')

        # Embedding dla URL
        url_embedding = Embedding(input_dim=n_urls, output_dim=self.embedding_dim)(url_input)
        url_embedding = Reshape((self.sequence_length, self.embedding_dim))(url_embedding)

        # Łączenie wszystkich wejść
        combined_input = Concatenate()([vusers_input, url_embedding, start_time_input, end_time_input])

        # Warstwy LSTM
        lstm_out = LSTM(128, return_sequences=True)(combined_input)
        lstm_out = Dropout(0.3)(lstm_out)
        lstm_out = LSTM(64)(lstm_out)
        lstm_out = Dropout(0.3)(lstm_out)

        # Warstwy gęste
        dense_out = Dense(32, activation='relu')(lstm_out)
        dense_out = Dropout(0.2)(dense_out)

        # Warstwa wyjściowa
        output = Dense(1)(dense_out)

        # Tworzenie modelu
        model = Model(
            inputs=[vusers_input, url_input, start_time_input, end_time_input],
            outputs=output
        )

        # Kompilacja modelu z optymalizatorem Adam
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        return model

    def _initialize_model(self, data):
        """Inicjalizuje model na podstawie danych."""
        if self.is_initialized:
            return

        # Kodowanie URL
        self.url_encoder.fit(data['URL'])
        n_urls = len(self.url_encoder.classes_)

        # Budowanie modelu
        self.model = self._build_model(n_urls)
        self.is_initialized = True

    def _save_encoders(self, path):
        """Zapisuje enkodery do pliku."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'url_encoder': self.url_encoder,
                'scaler_vusers': self.scaler_vusers,
                'scaler_response': self.scaler_response
            }, f)

    def _load_encoders(self, path):
        """Ładuje enkodery z pliku."""
        with open(path, 'rb') as f:
            encoders = pickle.load(f)
            self.url_encoder = encoders['url_encoder']
            self.scaler_vusers = encoders['scaler_vusers']
            self.scaler_response = encoders['scaler_response']
        self.is_initialized = True

    def save_model(self, model_path="model/complete_predictor.h5", encoders_path="model/encoders.pkl"):
        """Zapisuje model i enkodery do plików."""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        self.model.save(model_path)
        self._save_encoders(encoders_path)

    def prepare_input_data(self, data):
        """Przygotowuje dane wejściowe na podstawie DataFrame."""
        # Przygotowanie danych czasowych
        start_time_features = self._extract_time_features(data['StartTime'])
        end_time_features = self._extract_time_features(data['EndTime'])

        # Przygotowanie danych o liczbie użytkowników
        vusers_data = data['VusersNumber'].values.reshape(-1, 1)
        vusers_scaled = self.scaler_vusers.transform(vusers_data)

        # Kodowanie URL
        url_encoded = self.url_encoder.transform(data['URL'])

        return vusers_scaled, url_encoded, start_time_features, end_time_features

    def train(self, data, epochs=50, batch_size=32, validation_split=0.2):
        """
        Trenuje model na podstawie kompletnych danych.

        Args:
            data: DataFrame zawierający wszystkie kolumny: VusersNumber, URL, StartTime, EndTime, ResponseTime[ms]
            epochs: Liczba epok treningu
            batch_size: Rozmiar paczki danych
            validation_split: Część danych użyta do walidacji (0.0-1.0)
        """
        # Inicjalizacja modelu, jeśli jeszcze nie jest zainicjalizowany
        if not self.is_initialized:
            self._initialize_model(data)

        # Przekształcenie czasów do formatu datetime
        data['StartTime'] = pd.to_datetime(data['StartTime'], format='%H:%M:%S:%f')
        data['EndTime'] = pd.to_datetime(data['EndTime'], format='%H:%M:%S:%f')

        # Przygotowanie danych wejściowych
        vusers_scaled, url_encoded, start_time_features, end_time_features = self.prepare_input_data(data)

        # Przygotowanie danych wyjściowych (czas odpowiedzi)
        response_times = data['ResponseTime[ms]'].values.reshape(-1, 1)
        response_scaled = self.scaler_response.fit_transform(response_times)

        # Tworzenie sekwencji
        X_vusers, X_url, X_start_time, X_end_time, y = [], [], [], [], []

        for i in range(len(data) - self.sequence_length):
            X_vusers.append(vusers_scaled[i:i + self.sequence_length])
            X_url.append(url_encoded[i:i + self.sequence_length])
            X_start_time.append(start_time_features[i:i + self.sequence_length])
            X_end_time.append(end_time_features[i:i + self.sequence_length])
            y.append(response_scaled[i + self.sequence_length])

        if not X_vusers:
            print("Nie wystarczająco danych do treningu")
            return False

        # Konwersja do tablic numpy
        X_vusers = np.array(X_vusers)
        X_url = np.array(X_url)
        X_start_time = np.array(X_start_time)
        X_end_time = np.array(X_end_time)
        y = np.array(y)

        # Trening modelu
        history = self.model.fit(
            [X_vusers, X_url, X_start_time, X_end_time], y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )

        return history

    def predict(self, df_sequence):
        """
        Przewiduje czas odpowiedzi na podstawie sekwencji danych.

        Args:
            df_sequence: DataFrame zawierający sekwencję danych (co najmniej sequence_length wierszy)
                         z kolumnami: VusersNumber, URL, StartTime, EndTime

        Returns:
            Przewidywany czas odpowiedzi
        """
        if len(df_sequence) < self.sequence_length:
            raise ValueError(f"Sekwencja musi zawierać co najmniej {self.sequence_length} wierszy")

        # Użyj tylko ostatnich sequence_length wierszy
        df_sequence = df_sequence.iloc[-self.sequence_length:]

        # Przygotowanie danych wejściowych
        df_sequence['StartTime'] = pd.to_datetime(df_sequence['StartTime'], format='%H:%M:%S:%f')
        df_sequence['EndTime'] = pd.to_datetime(df_sequence['EndTime'], format='%H:%M:%S:%f')

        vusers_scaled, url_encoded, start_time_features, end_time_features = self.prepare_input_data(df_sequence)

        # Przekształcenie do formatu odpowiedniego dla modelu
        vusers_input = vusers_scaled.reshape(1, self.sequence_length, 1)
        url_input = url_encoded.reshape(1, self.sequence_length)
        start_time_input = start_time_features.reshape(1, self.sequence_length, 6)
        end_time_input = end_time_features.reshape(1, self.sequence_length, 6)

        # Predykcja
        prediction = self.model.predict([vusers_input, url_input, start_time_input, end_time_input])

        # Odwrócenie skalowania
        return self.scaler_response.inverse_transform(prediction)[0][0]