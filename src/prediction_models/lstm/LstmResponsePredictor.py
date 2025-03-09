import numpy as np
import os
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import pandas as pd


class LstmResponsePredictor:
    def __init__(self, sequence_length=5, model_path=None):
        self.sequence_length = sequence_length
        self.scaler_vusers = MinMaxScaler(feature_range=(0, 1))
        self.scaler_response = MinMaxScaler(feature_range=(0, 1))
        if model_path and os.path.exists(model_path):
            self.model = load_model(model_path)
        else:
            self.model = self._build_model()
        self.history = []

    def _build_model(self):
        model = Sequential()
        model.add(LSTM(50, return_sequences=True, input_shape=(self.sequence_length, 2)))
        model.add(LSTM(50))
        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mse')
        return model

    def save_model(self, path="model/lstm_predictor.h5"):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(path)

    def train(self, vusers_data, response_times, epochs=50, batch_size=32):
        X, y = self._prepare_data(vusers_data, response_times)
        if X.size == 0 or y.size == 0:
            print("Not enough data for training")
            return False

        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)
        return True

    def predict_response_time(self, vusers_sequence):
        if len(vusers_sequence) < self.sequence_length:
            pad_length = self.sequence_length - len(vusers_sequence)
            padded_vusers = np.pad(vusers_sequence, (pad_length, 0), 'edge')
        else:
            padded_vusers = vusers_sequence[-self.sequence_length:]

        fake_response = np.zeros_like(padded_vusers)

        input_seq = np.column_stack((
            self.scaler_vusers.transform(padded_vusers.reshape(-1, 1)).flatten(),
            self.scaler_response.transform(fake_response.reshape(-1, 1)).flatten()
        )).reshape(1, self.sequence_length, 2)

        prediction = self.model.predict(input_seq)
        return self.scaler_response.inverse_transform(prediction)[0][0]

    def predict_optimal_vusers(self, target_response_time_ms, current_vusers, max_increase=20):
        best_vusers = current_vusers
        min_diff = float('inf')

        for test_vusers in range(current_vusers, current_vusers + max_increase + 1, 5):
            test_sequence = np.array([test_vusers] * self.sequence_length).reshape(-1, 1)
            predicted_response = self.predict_response_time(test_sequence)

            diff = abs(predicted_response - target_response_time_ms)

            if diff < min_diff:
                min_diff = diff
                best_vusers = test_vusers

            if predicted_response > target_response_time_ms:
                break

        return best_vusers

    def update_with_result(self, vusers, response_time):
        self.history.append((vusers, response_time))

    def _prepare_data(self, vusers_data, response_times):
        vusers_scaled = self.scaler_vusers.fit_transform(vusers_data)
        response_scaled = self.scaler_response.fit_transform(response_times)

        X, y = [], []

        for i in range(len(vusers_scaled) - self.sequence_length):
            seq = np.column_stack((
                vusers_scaled[i:i + self.sequence_length],
                response_scaled[i:i + self.sequence_length]
            )).reshape(self.sequence_length, 2)

            target = response_scaled[i + self.sequence_length]

            X.append(seq)
            y.append(target)

        if not X:
            return np.array([]), np.array([])

        return np.array(X), np.array(y)

    def evaluate_predictions(self, vusers_data, actual_response_times, save_csv=True, visualize=True,
                             output_path="./src/results/predictions.csv"):
        """Evaluate model predictions against actual data and optionally visualize results.

        Args:
            vusers_data: Array of virtual user counts [[v1], [v2], ...]
            actual_response_times: Array of actual response times [[r1], [r2], ...]
            save_csv: Whether to export results to CSV
            visualize: Whether to launch visualization dashboard
            output_path: Path to save prediction results CSV

        Returns:
            DataFrame with prediction results or None
        """
        from src.utils.export_utils import export_predictions_to_csv

        # Export predictions to CSV
        df = None
        if save_csv:
            df = export_predictions_to_csv(self, vusers_data, actual_response_times, output_path)

        # Launch visualization dashboard
        if visualize:
            from src.visualization import prediction_visualizer
            print("Starting visualization dashboard. Press Ctrl+C to exit.")
            prediction_visualizer.run_dashboard(output_path)

        return df