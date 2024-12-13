# ARIMA Model Implementation
import os
from datetime import timedelta

import pandas as pd
from statsmodels.sandbox.mle import data
from statsmodels.tsa.arima_model import ARIMA

# Load data
current_dir = os.path.dirname(__file__)
results_file = os.path.join(current_dir, 'results', 'results.csv')

# Preprocess data
data['EndTime'] = pd.to_datetime(data['EndTime'], format='%H:%M:%S:%f')
data['ResponseTime[ms]'] = data['ResponseTime[ms]'].astype(float)

# Train ARIMA model on ResponseTime
response_times = data['ResponseTime[ms]']
model = ARIMA(response_times, order=(5, 1, 0))
model_fit = model.fit()

# Make predictions for the next 20 seconds
predictions = model_fit.forecast(steps=30)

# Generate predicted EndTime
last_end_time = data['EndTime'].iloc[-1]
predicted_end_times = [last_end_time + timedelta(seconds=i) for i in range(1, 21)]

# Save predictions to predicted_results.csv
predicted_data = pd.DataFrame({
    'EndTime': predicted_end_times,
    'ResponseTime[ms]': predictions
})
predicted_data.to_csv('predicted_results.csv', index=False)