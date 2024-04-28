import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px


class Monitoring:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.app = dash.Dash(__name__)
        self.df = None
        self.setup_app()

    def load_data(self):
        self.df = pd.read_csv(self.csv_file)

        # Przetwarzanie kolumn czasu
        self.df['StartTime'] = pd.to_datetime(self.df['StartTime'], format='%H:%M:%S:%f')
        self.df['EndTime'] = pd.to_datetime(self.df['EndTime'], format='%H:%M:%S:%f')

    def setup_app(self):
        self.load_data()

        self.app.layout = html.Div(children=[
            html.H1(children='Monitoring aktywnych użytkowników'),

            dcc.Graph(id='active-users-graph'),
            dcc.Graph(id='response-time-graph'),  # Nowy komponent dla wykresu ResponseTime

            dcc.Interval(
                id='interval-component',
                interval=1 * 1000,  # in milliseconds
                n_intervals=0
            )
        ])

        @self.app.callback(
            Output('active-users-graph', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_active_users_graph(n):
            fig = px.line(self.df, x="StartTime", y="VusersNumber", title="Aktywni użytkownicy w czasie")
            fig.update_xaxes(tickformat="%H:%M:%S")
            fig.update_xaxes(dtick=1000, tick0=self.df['StartTime'].min())
            return fig

        @self.app.callback(
            Output('response-time-graph', 'figure'),
            Input('interval-component', 'n_intervals')
        )
        def update_response_time_graph(n):
            fig = px.line(self.df, x="EndTime", y="ResponseTime[ms]", title="Czas odpowiedzi w czasie")
            fig.update_xaxes(tickformat="%H:%M:%S")
            fig.update_xaxes(dtick=1000, tick0=self.df['EndTime'].min())
            return fig

    def run(self):
        self.app.run_server(debug=True)


if __name__ == '__main__':
    monitoring = Monitoring('results.csv')
    monitoring.run()
