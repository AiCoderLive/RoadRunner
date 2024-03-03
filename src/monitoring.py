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

    def setup_app(self):
        self.load_data()

        self.app.layout = html.Div(children=[
            html.H1(children='Monitoring aktywnych użytkowników'),

            dcc.Graph(id='active-users-graph'),

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
        def update_graph(n):
            filtered_df = self.df  # Tutaj można dodać filtrację w czasie, jeśli trzeba
            fig = px.line(filtered_df, x="StartTime", y="VuserNumber", title="Aktywni użytkownicy w czasie")
            return fig

    def run(self):
        self.app.run_server(debug=True)


if __name__ == '__main__':
    monitoring = Monitoring('results.csv')
    monitoring.run()
