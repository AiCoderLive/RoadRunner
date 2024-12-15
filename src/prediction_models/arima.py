# ARIMA Model Implementation
from datetime import timedelta

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

from src.utils.Paths import get_results_csv_file

# Load data
data = pd.read_csv(get_results_csv_file())

# Preprocess data
data['EndTime'] = pd.to_datetime(data['EndTime'], format='%H:%M:%S:%f')
data['ResponseTime[ms]'] = data['ResponseTime[ms]'].astype(float)

# Train ARIMA model on ResponseTime
response_times = data['ResponseTime[ms]']
model = ARIMA(response_times, order=(5, 1, 0))

# Increase the number of iterations for the optimization process
model_fit = model.fit(method_kwargs={'maxiter': 500})

# Make predictions for the next 20 seconds
predictions = model_fit.forecast(steps=20)

# Generate predicted EndTime
last_end_time = data['EndTime'].iloc[-1]
predicted_end_times = [last_end_time + timedelta(seconds=i) for i in range(1, 21)]

# Save predictions to predicted_results.csv
predicted_data = pd.DataFrame({
    'EndTime': predicted_end_times,
    'ResponseTime[ms]': predictions
})
predicted_data.to_csv('predicted_results.csv', index=False)