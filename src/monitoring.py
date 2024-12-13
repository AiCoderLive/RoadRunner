import os

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import argparse

from src.prediction_models.arima import current_dir


class Monitoring:
    def __init__(self, csv_file, use_interval=True):
        self.csv_file = csv_file
        self.use_interval = use_interval
        self.app = dash.Dash(__name__)
        self.df = None
        self.predicted_df = None
        self.setup_app()

    def load_data(self):
        try:
            self.df = pd.read_csv(self.csv_file)
            self.process_data()
        except FileNotFoundError:
            print(f"Error: File {self.csv_file} not found.")
            exit(1)

    def load_predicted_data(self):
        try:
            self.predicted_df = os.path.join(current_dir, 'results', 'predicted_results.csv')
            self.predicted_df['EndTime'] = pd.to_datetime(self.predicted_df['EndTime'], format='%H:%M:%S')
        except FileNotFoundError:
            print("Error: File predicted_results.csv not found.")
            exit(1)

    def process_data(self):
        self.df['StartTime'] = pd.to_datetime(self.df['StartTime'], format='%H:%M:%S:%f')
        self.df['EndTime'] = pd.to_datetime(self.df['EndTime'], format='%H:%M:%S:%f')

    def setup_app(self):
        self.load_data()
        self.load_predicted_data()
        self.app.layout = self.create_layout()
        if self.use_interval:
            self.setup_callbacks()

    def create_layout(self):
        layout_children = [
            html.H1(children='Monitoring aktywnych użytkowników'),
            dcc.Graph(id='active-users-graph', figure=self.create_active_users_graph()),
            dcc.Graph(id='response-time-graph', figure=self.create_response_time_graph()),
            dcc.Graph(id='predicted-response-time-graph', figure=self.create_predicted_response_time_graph())
        ]
        if self.use_interval:
            layout_children.append(
                dcc.Interval(
                    id='interval-component',
                    interval=1 * 1000,  # in milliseconds
                    n_intervals=0
                )
            )
        return html.Div(children=layout_children)

    def setup_callbacks(self):
        @self.app.callback(
            Output('active-users-graph', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_active_users_graph(n):
            return self.create_active_users_graph()

        @self.app.callback(
            Output('response-time-graph', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_response_time_graph(n):
            return self.create_response_time_graph()

        @self.app.callback(
            Output('predicted-response-time-graph', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_predicted_response_time_graph(n):
            return self.create_predicted_response_time_graph()

    def create_active_users_graph(self, title="Aktywni użytkownicy w czasie", xaxis_format="%H:%M:%S", dtick=1000):
        fig = px.line(self.df, x="StartTime", y="VusersNumber", title=title)
        fig.update_xaxes(tickformat=xaxis_format)
        fig.update_xaxes(dtick=dtick, tick0=self.df['StartTime'].min())
        return fig

    def create_response_time_graph(self, title="Czas odpowiedzi w czasie", xaxis_format="%H:%M:%S", dtick=1000):
        fig = px.line(self.df, x="EndTime", y="ResponseTime[ms]", title=title)
        fig.update_xaxes(tickformat=xaxis_format)
        fig.update_xaxes(dtick=dtick, tick0=self.df['EndTime'].min())
        return fig

    def create_predicted_response_time_graph(self, title="Przewidywany czas odpowiedzi w czasie", xaxis_format="%H:%M:%S", dtick=1000):
        fig = px.line(self.df, x="EndTime", y="ResponseTime[ms]", title=title, color_discrete_sequence=['blue'])
        fig.add_scatter(x=self.predicted_df['EndTime'], y=self.predicted_df['ResponseTime[ms]'], mode='lines', name='Predicted Response Time', line=dict(color='red'))
        fig.update_xaxes(tickformat=xaxis_format)
        fig.update_xaxes(dtick=dtick, tick0=self.df['EndTime'].min())
        return fig

    def run(self):
        self.app.run_server(debug=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Monitoring app.')
    parser.add_argument('csv_file', type=str, help='Path to the CSV file.')
    parser.add_argument('--use_interval', action='store_true', help='Enable interval refresh.')
    args = parser.parse_args()

    monitoring = Monitoring(args.csv_file, use_interval=args.use_interval)
    monitoring.run()