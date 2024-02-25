from dash import dcc, html, dash
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=1 * 1000,  # in milliseconds
        n_intervals=0
    )
])


@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):
    df = pd.read_csv('results.csv')  # Ensure the file path matches where PerformanceTester.py writes data
    # Example logic to plot data (modify according to your data structure)
    if not df.empty:
        figure = go.Figure(
            data=[go.Scatter(x=df.index, y=df['ResponseTime'], mode='lines+markers')],
            layout=go.Layout(title="Response Time Over Time", xaxis=dict(title='Request'),
                             yaxis=dict(title='Response Time (ms)'))
        )
    else:
        figure = go.Figure()  # Return an empty figure if no data is available
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
