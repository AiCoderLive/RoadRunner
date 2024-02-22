# Zapisz ten kod jako monitoring.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd

import pandas as pd
from dateutil.parser import parse


# Funkcja do parsowania daty i czasu
def parse_date(x):
    return parse(x)


# Wczytanie danych z pliku CSV, daty i godziny jako typ 'object'
df = pd.read_csv('test_results.csv', dtype={'StartTime': 'object', 'EndTime': 'object'})

# Konwersja na typ daty i godziny z określeniem formatu
df['StartTime'] = pd.to_datetime(df['StartTime'], format='%H:%M:%S')
df['EndTime'] = pd.to_datetime(df['EndTime'], format='%H:%M:%S')

# Rozpoczęcie aplikacji Dash
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Aktywni użytkownicy w czasie'),
    dcc.Graph(id='active-users-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,  # in milliseconds
        n_intervals=0
    )
])


@app.callback(Output('active-users-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    # Przygotowanie danych
    # Generowanie listy unikalnych sekund z zakresu czasu testu
    time_range = pd.date_range(df['StartTime'].min(), df['EndTime'].max(), freq='s')

    active_users = []
    for time in time_range:
        # Liczenie aktywnych użytkowników w danej sekundzie
        active_count = df[(df['StartTime'] <= time) & (df['EndTime'] > time)].shape[0]
        active_users.append(active_count)

    # Tworzenie wykresu
    trace = go.Scatter(x=time_range, y=active_users, mode='lines+markers', name='Aktywni użytkownicy')
    layout = go.Layout(title='Aktywni użytkownicy w czasie', xaxis=dict(title='Czas'),
                       yaxis=dict(title='Liczba aktywnych użytkowników'))
    return {'data': [trace], 'layout': layout}


if __name__ == '__main__':
    app.run_server(debug=True)
