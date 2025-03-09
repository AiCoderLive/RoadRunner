import concurrent.futures
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from functools import partial
import os
import multiprocessing
from datetime import datetime, timedelta

# Determine correct paths based on script location
current_dir = os.path.dirname(os.path.abspath(__file__))
results_file = os.path.join(current_dir, "results", "results.csv")
visualization_path = os.path.join(current_dir, "results", "prediction_visualization.png")
csv_output_path = os.path.join(current_dir, "results", "extended_predictions.csv")


# Function to predict response time for a given virtual user count
def predict_for_vuser(v, predictor):
    vuser_sequence = np.array([v[0]] * predictor.sequence_length).reshape(-1, 1)
    return predictor.predict_response_time(vuser_sequence)


def main():
    # Debug info
    print(f"Looking for results file at: {results_file}")
    print(f"Current directory: {os.getcwd()}")

    # Load your existing results
    results_df = pd.read_csv(results_file)

    # Check if EndTime column exists, if not create a synthetic time series
    if 'EndTime' not in results_df.columns:
        # Create synthetic timestamps (one every minute)
        start_time = datetime.now() - timedelta(minutes=len(results_df))
        times = [start_time + timedelta(minutes=i) for i in range(len(results_df))]
        results_df['EndTime'] = times
    else:
        # Convert the time format by replacing the last colon with a period
        try:
            results_df['EndTime'] = results_df['EndTime'].astype(str).str.replace(
                r'(\d+):(\d+):(\d+):(\d+)', r'\1:\2:\3.\4', regex=True)

            # Add today's date since these appear to be just times
            base_date = datetime.now().strftime('%Y-%m-%d ')
            results_df['EndTime'] = pd.to_datetime(
                base_date + results_df['EndTime'],
                format='%Y-%m-%d %H:%M:%S.%f',
                errors='coerce'
            )

            # If any parsing failed, fill with synthetic times
            if results_df['EndTime'].isna().any():
                raise ValueError("Some timestamps could not be parsed")

        except Exception as e:
            print(f"Error parsing timestamps: {e}")
            # Fall back to synthetic timestamps
            start_time = datetime.now() - timedelta(minutes=len(results_df))
            times = [start_time + timedelta(minutes=i) for i in range(len(results_df))]
            results_df['EndTime'] = times

    # Extract data
    vusers = results_df['VusersNumber'].values.reshape(-1, 1)
    responses = results_df['ResponseTime[ms]'].values.reshape(-1, 1)
    times = results_df['EndTime'].values

    # Create and train the predictor
    from prediction_models.lstm.LstmResponsePredictor import LstmResponsePredictor

    predictor = LstmResponsePredictor(sequence_length=5)
    predictor.train(vusers, responses, epochs=50)

    # Create a sequence for future prediction (extending by 30% more time points)
    max_vusers = int(vusers.max())
    last_time = results_df['EndTime'].max()

    # For predictions, assume the future will continue the same VUsers pattern
    future_times = []
    future_vusers = []

    # Create future data points (30% more)
    future_points = int(len(results_df) * 0.3)
    time_delta = (results_df['EndTime'].max() - results_df['EndTime'].min()) / len(results_df)

    for i in range(1, future_points + 1):
        # Create future timestamp
        future_time = last_time + i * time_delta
        future_times.append(future_time)

        # For demo purposes, use a formula that gradually increases
        future_vuser = max_vusers * (1 + (i / future_points) * 0.5)
        future_vusers.append(int(future_vuser))

    future_vusers_array = np.array(future_vusers).reshape(-1, 1)

    # Make predictions for both historical and future data
    with concurrent.futures.ProcessPoolExecutor(max_workers=20) as executor:
        predict_func = partial(predict_for_vuser, predictor=predictor)

        # Predict for historical data
        historical_predictions = list(executor.map(predict_func, vusers))

        # Predict for future data
        future_predictions = list(executor.map(predict_func, future_vusers_array))

    historical_predictions = np.array(historical_predictions)
    future_predictions = np.array(future_predictions)

    # Combine all timestamps for plotting
    all_times = np.concatenate([times, future_times])
    all_vusers = np.concatenate([vusers.flatten(), future_vusers_array.flatten()])
    all_responses = np.concatenate([historical_predictions.flatten(), future_predictions.flatten()])

    # Create two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 12))

    # Plot 1: Time vs VUsers
    ax1.plot(times, vusers.flatten(), 'b-', label='Actual VUsers')
    ax1.plot(future_times, future_vusers_array.flatten(), 'r-', label='Predicted VUsers')
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Virtual Users')
    ax1.set_title('Actual vs Predicted Virtual Users Over Time')
    ax1.legend()
    ax1.grid(True)

    # Plot 2: Time vs Response Time
    ax2.plot(times, responses.flatten(), 'b-', label='Actual Response Time')
    ax2.plot(times, historical_predictions.flatten(), 'r--', label='Predicted Response Time (Historical)')
    ax2.plot(future_times, future_predictions.flatten(), 'r-', label='Predicted Response Time (Future)')
    ax2.set_xlabel('Time')
    ax2.set_ylabel('Response Time (ms)')
    ax2.set_title('Actual vs Predicted Response Times Over Time')
    ax2.legend()
    ax2.grid(True)

    # Format date on x-axis if we have datetime objects
    if isinstance(all_times[0], (datetime, np.datetime64, pd.Timestamp)):
        date_format = DateFormatter('%H:%M:%S')
        ax1.xaxis.set_major_formatter(date_format)
        ax2.xaxis.set_major_formatter(date_format)
        fig.autofmt_xdate()

    plt.tight_layout()
    plt.savefig(visualization_path)
    plt.show()

    # Save predictions to CSV
    prediction_df = pd.DataFrame({
        'time': all_times,
        'vusers': all_vusers,
        'response_time': all_responses,
        'type': ['actual'] * len(times) + ['predicted'] * len(future_times)
    })
    prediction_df.to_csv(csv_output_path, index=False)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()