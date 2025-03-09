import os
import pandas as pd
import numpy as np

def export_predictions_to_csv(predictor, vusers_data, actual_response_times, output_path="./src/results/predictions.csv"):
    """Export actual and predicted response times to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    predictions = []
    for i in range(len(vusers_data) - predictor.sequence_length):
        input_sequence = vusers_data[i:i+predictor.sequence_length]
        predicted_time = predictor.predict_response_time(input_sequence)
        actual_time = actual_response_times[i+predictor.sequence_length]

        predictions.append({
            "vusers": vusers_data[i+predictor.sequence_length][0],
            "actual_response_time": actual_time[0],
            "predicted_response_time": predicted_time,
            "prediction_error": predicted_time - actual_time[0]
        })

    df = pd.DataFrame(predictions)
    df.to_csv(output_path, index=False)
    print(f"Predictions exported to {output_path}")
    return df