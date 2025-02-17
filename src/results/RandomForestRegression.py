import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score


def load_and_prepare_data(file_path):
    data = pd.read_csv(file_path)
    data['StartTime'] = pd.to_datetime(data['StartTime'], format='%H:%M:%S:%f')
    data['EndTime'] = pd.to_datetime(data['EndTime'], format='%H:%M:%S:%f')
    return data


def train_model(data):
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(data[['VusersNumber']], data['ResponseTime[ms]'])
    return rf_model


def get_predictions(model, user_counts):
    return model.predict([[x] for x in user_counts])


def create_visualization(data, user_counts, predictions):
    last_time = data['EndTime'].iloc[-1]
    prediction_times = pd.date_range(start=last_time, periods=len(user_counts), freq='2min')

    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=('Aktywni użytkownicy w czasie',
                                        'Czas odpowiedzi w czasie'))

    # Users plot
    fig.add_trace(go.Scatter(x=data['StartTime'], y=data['VusersNumber'],
                             mode='lines', name='Użytkownicy'), row=1, col=1)
    fig.add_trace(go.Scatter(x=prediction_times, y=user_counts,
                             mode='lines', name='Predykcje użytkowników',
                             line=dict(color='red')), row=1, col=1)

    # Response time plot
    fig.add_trace(go.Scatter(x=data['EndTime'], y=data['ResponseTime[ms]'],
                             mode='lines', name='Czas odpowiedzi'), row=2, col=1)
    fig.add_trace(go.Scatter(x=prediction_times, y=predictions,
                             mode='lines', name='Predykcje czasów',
                             line=dict(color='red')), row=2, col=1)

    fig.update_layout(height=800)
    return fig


def print_predictions(user_counts, predictions):
    for users, pred in zip(user_counts, predictions):
        print(f'Przewidywany czas odpowiedzi dla {users} użytkowników: {pred:.2f} ms')


def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    return rmse, r2


def main():
    # Load data
    data = load_and_prepare_data('results.csv')

    # Prepare train-test split
    X = data[['VusersNumber']]
    y = data['ResponseTime[ms]']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    model = train_model(data)

    # Get predictions for specific user counts
    user_counts = [120, 140, 160, 180, 200]
    predictions = get_predictions(model, user_counts)

    # Create and show visualization
    fig = create_visualization(data, user_counts, predictions)
    fig.show()

    # Print predictions
    print_predictions(user_counts, predictions)

    # Evaluate model
    rmse, r2 = evaluate_model(model, X_test, y_test)
    print(f'\nModel Evaluation:')
    print(f'RMSE: {rmse:.2f}')
    print(f'R2 Score: {r2:.2f}')


if __name__ == "__main__":
    main()