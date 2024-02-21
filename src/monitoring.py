import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import numpy as np


class Monitoring:
    def __init__(self, filename):
        self.filename = filename
        self.app = dash.Dash(__name__)
        self.setup_app()

    def load_data(self):
        data = pd.read_csv(self.filename)
        data['StartTime'] = pd.to_datetime(data['StartTime'], format='%H:%M:%S:%f')
        # Count the number of requests per second
        data['Second'] = data['StartTime'].dt.floor('s')
        data_count = data.groupby('Second').size().reset_index(name='Counts')
        return data_count

    def setup_app(self):
        self.app.layout = html.Div([
            dcc.Graph(id='live-update-graph'),
            dcc.Interval(
                id='interval-component',
                interval=1 * 1000,  # in milliseconds
                n_intervals=0
            )
        ])

        @self.app.callback(Output('live-update-graph', 'figure'),
                           Input('interval-component', 'n_intervals'))
        def update_graph_live(n):
            data_count = self.load_data()
            # Create the figure with the new data
            fig = px.line(data_count, x='Second', y='Counts', title='Liczba requestów na sekundę')
            return fig

    def run(self):
        self.app.run_server(debug=True)


# Create an instance of the Monitoring class
monitoring = Monitoring('results.csv')
monitoring.run()
