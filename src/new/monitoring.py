import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Wczytywanie danych z pliku CSV
df = pd.read_csv('C:\\Repo\\GitHub\\RoadRunner\\src\\new\\results.csv')  # Zaktualizowana ścieżka do pliku

# Konwersja kolumn StartTime i EndTime do formatu datetime
df['StartTime'] = pd.to_datetime(df['StartTime'], format='%H:%M:%S')
df['EndTime'] = pd.to_datetime(df['EndTime'], format='%H:%M:%S')


class PerformanceTestVisualizer:
    def __init__(self, data_frame):
        self.df = data_frame
        self.app = Dash(__name__)
        self.setup_layout()

    def setup_layout(self):
        self.app.layout = html.Div(children=[
            html.H1(children='Performance Test Visualization'),
            dcc.Graph(id='performance-graph')
        ])

        @self.app.callback(
            Output('performance-graph', 'figure'),
            Input('performance-graph', 'id')
        )
        def update_graph(_):
            # Przygotowanie danych z uwzględnieniem przerw
            self.df['Time'] = self.df['StartTime'].dt.strftime('%H:%M:%S')
            # Grupowanie danych po czasie
            grouped_data = self.df.groupby('Time').size().reset_index(name='Requests')
            # Dodanie obsługi przerw
            grouped_data['Time'] = pd.to_datetime(grouped_data['Time'], format='%H:%M:%S')
            grouped_data = grouped_data.set_index('Time').resample('s').asfreq().fillna(0).reset_index()
            grouped_data['Time'] = grouped_data['Time'].dt.strftime('%H:%M:%S')

            # Tworzenie wykresu
            figure = px.line(grouped_data, x='Time', y='Requests', title='Active Requests Over Time',
                             labels={'Time': 'Time (HH:MM:SS)', 'Requests': 'Number of Active Requests'})
            return figure

    def run(self):
        self.app.run_server(debug=True)


# Uruchomienie wizualizacji
visualizer = PerformanceTestVisualizer(df)
visualizer.run()
