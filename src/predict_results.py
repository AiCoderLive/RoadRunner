# After scenario execution completes
import pandas as pd
import numpy as np
from src.prediction_models.lstm.LstmResponsePredictor import LstmResponsePredictor
from src.utils.Scenario import Scenario

# Load results
results_df = pd.read_csv(Scenario.results_file)
vusers = results_df['VusersNumber'].values.reshape(-1, 1)
responses = results_df['ResponseTime[ms]'].values.reshape(-1, 1)

# Train model and visualize
predictor = LstmResponsePredictor()
predictor.train(vusers, responses, epochs=50)
predictor.evaluate_predictions(vusers, responses)