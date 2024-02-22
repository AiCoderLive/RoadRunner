# monitoring.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import datetime

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
    try:
        df = pd.read_csv('results.csv')
        df['StartTime'] = pd.to_datetime(df['StartTime'], format='%H:%M:%S')
    except:
        df = pd.DataFrame(columns=['StartTime', 'EndTime', 'ResponseTime'])

    data = {
        'time': df['StartTime'],
        'users': range(len(df))
    }
    fig = go.Figure([
        go.Scatter(x=data['time'], y=data['users'], mode='lines+markers')
    ])
    fig.update_layout(title='Requests over Time',
                      xaxis_title='Time',
                      yaxis_title='Number of Users',
                      xaxis=dict(range=[min(data['time']), max(data['time']) + datetime.timedelta(seconds=1)]))
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
