import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import os


def create_prediction_dashboard(predictions_csv="./src/results/predictions.csv"):
    """Create and run a Dash dashboard for visualizing prediction results."""
    # Check if file exists
    if not os.path.exists(predictions_csv):
        raise FileNotFoundError(f"Prediction CSV file not found: {predictions_csv}")

    # Load prediction data
    df = pd.read_csv(predictions_csv)

    # Create Dash application
    app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    app.layout = dbc.Container([
        html.H1("Response Time Prediction Dashboard"),

        dbc.Row([
            dbc.Col([
                html.H3("Virtual Users vs Response Times"),
                dcc.Graph(id='prediction-graph'),
            ], width=12)
        ]),

        dbc.Row([
            dbc.Col([
                html.H3("Prediction Error Analysis"),
                dcc.Graph(id='error-graph'),
            ], width=12)
        ]),

        dbc.Row([
            dbc.Col([
                html.H4("Filter Data Range:"),
                dcc.RangeSlider(
                    id='vuser-range',
                    min=df['vusers'].min(),
                    max=df['vusers'].max(),
                    value=[df['vusers'].min(), df['vusers'].max()],
                    marks={i: str(i) for i in range(int(df['vusers'].min()), int(df['vusers'].max()) + 1, 20)},
                    step=1
                ),
            ], width=12)
        ]),
    ], fluid=True)

    @app.callback(
        [Output('prediction-graph', 'figure'),
         Output('error-graph', 'figure')],
        [Input('vuser-range', 'value')]
    )
    def update_graphs(vuser_range):
        filtered_df = df[(df['vusers'] >= vuser_range[0]) & (df['vusers'] <= vuser_range[1])]

        # Create prediction comparison graph
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=filtered_df['vusers'],
            y=filtered_df['actual_response_time'],
            mode='lines+markers',
            name='Actual Response Time'
        ))
        fig1.add_trace(go.Scatter(
            x=filtered_df['vusers'],
            y=filtered_df['predicted_response_time'],
            mode='lines+markers',
            name='Predicted Response Time'
        ))
        fig1.update_layout(
            xaxis_title='Virtual Users',
            yaxis_title='Response Time (ms)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )

        # Create error analysis graph
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=filtered_df['vusers'],
            y=filtered_df['prediction_error'],
            name='Prediction Error'
        ))
        fig2.update_layout(
            xaxis_title='Virtual Users',
            yaxis_title='Error (ms)',
            title='Prediction Error (Predicted - Actual)'
        )

        return fig1, fig2

    return app


def run_dashboard(predictions_csv="./src/results/predictions.csv"):
    """Create and run the prediction dashboard."""
    app = create_prediction_dashboard(predictions_csv)
    app.run_server(debug=True)


if __name__ == '__main__':
    run_dashboard()