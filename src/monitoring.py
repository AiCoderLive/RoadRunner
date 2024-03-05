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
        # Określenie formatu czasu; przykład zakłada, że 'StartTime' jest w formacie 'godzina:minuta:sekunda:milisekundy'
        # Należy dostosować format do rzeczywistego formatu danych w pliku CSV
        self.df['StartTime'] = pd.to_datetime(self.df['StartTime'], format='%H:%M:%S:%f')

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
            filtered_df = self.df
            fig = px.line(filtered_df, x="StartTime", y="VuserNumber", title="Aktywni użytkownicy w czasie")

            # Ustawienie formatu osi X bez milisekund
            fig.update_xaxes(tickformat="%H:%M:%S")

            # Ustawienie formatu osi X do sekund za pomocą 'dtick'
            fig.update_xaxes(
                dtick=1000,  # interwał co 1 sekundę w milisekundach
                tick0=self.df['StartTime'].min()  # punkt startowy
            )

            return fig

    def run(self):
        self.app.run_server(debug=True)


if __name__ == '__main__':
    monitoring = Monitoring('results.csv')
    monitoring.run()
