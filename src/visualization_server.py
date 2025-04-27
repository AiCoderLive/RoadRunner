#!/usr/bin/env python3
"""
Serwer wizualizacji wyników testów wydajnościowych wraz z predykcjami LSTM.
"""
import os
import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from src.utils.Paths import get_results_csv_file
from src.prediction_models.lstm.lstm_trainer import predict_response_time, calculate_optimal_vusers

# Konfiguracja aplikacji Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Kolory dla wykresów
COLORS = {
    'actual': 'blue',
    'predicted': 'red',
    'background': '#f8f9fa',
    'text': '#212529'
}


def wait_for_files():
    """Oczekuje na pojawienie się niezbędnych plików"""
    results_file = get_results_csv_file()
    prediction_file = "./src/results/predictions.csv"

    files_exist = False
    retries = 0
    max_retries = 30

    while not files_exist and retries < max_retries:
        results_exists = os.path.exists(results_file) and os.path.getsize(results_file) > 0
        predictions_exists = os.path.exists(prediction_file) and os.path.getsize(prediction_file) > 0

        if results_exists:
            print(f"Znaleziono plik wyników: {results_file}")
            # Jeśli plik predykcji nie istnieje, to można kontynuować z samymi wynikami
            files_exist = True
        else:
            print(f"Czekam na pliki danych (próba {retries + 1}/{max_retries})...")
            retries += 1
            time.sleep(10)

    return results_exists, os.path.exists(prediction_file) and os.path.getsize(prediction_file) > 0


def load_data():
    """Wczytuje dane z plików CSV."""
    results_file = get_results_csv_file()
    prediction_file = "./src/results/predictions.csv"

    data = None
    predictions = None

    # Wczytaj wyniki testów
    if os.path.exists(results_file):
        try:
            data = pd.read_csv(results_file)
            data['StartTime'] = pd.to_datetime(data['StartTime'], format='%H:%M:%S:%f')
            data['EndTime'] = pd.to_datetime(data['EndTime'], format='%H:%M:%S:%f')
            print(f"Wczytano {len(data)} rekordów z pliku wyników.")
        except Exception as e:
            print(f"Błąd podczas wczytywania pliku wyników: {e}")

    # Wczytaj predykcje LSTM jeśli istnieją
    if os.path.exists(prediction_file):
        try:
            predictions = pd.read_csv(prediction_file)
            print(f"Wczytano {len(predictions)} rekordów z pliku predykcji.")
        except Exception as e:
            print(f"Błąd podczas wczytywania pliku predykcji: {e}")

    return data, predictions


def create_active_users_graph(data):
    """Tworzy wykres aktywnych użytkowników w czasie."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data['StartTime'],
        y=data['VusersNumber'],
        mode='lines',
        name='Aktywni użytkownicy',
        line=dict(color=COLORS['actual'])
    ))

    fig.update_layout(
        title='Aktywni użytkownicy w czasie',
        xaxis_title='Czas',
        yaxis_title='Liczba użytkowników',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font=dict(color=COLORS['text'])
    )

    return fig


def create_response_time_graph(data, predictions=None):
    """Tworzy wykres czasu odpowiedzi w czasie."""
    fig = go.Figure()

    # Wykres rzeczywistych czasów odpowiedzi
    fig.add_trace(go.Scatter(
        x=data['EndTime'],
        y=data['ResponseTime[ms]'],
        mode='lines',
        name='Rzeczywisty czas odpowiedzi',
        line=dict(color=COLORS['actual'])
    ))

    # Dodaj predykcje jeśli są dostępne
    if predictions is not None:
        try:
            # Jeśli w danych są kolumny 'actual_response_time' i 'predicted_response_time'
            if 'actual_response_time' in predictions.columns and 'predicted_response_time' in predictions.columns:
                # Mapuj predykcje do najbliższego czasu z danych rzeczywistych
                # To jest uproszczone podejście
                merged_data = pd.merge_asof(
                    data.sort_values('VusersNumber'),
                    predictions.sort_values('vusers')[['vusers', 'predicted_response_time']],
                    left_on='VusersNumber',
                    right_on='vusers',
                    direction='nearest'
                )

                # Dodaj przewidywane czasy odpowiedzi
                fig.add_trace(go.Scatter(
                    x=merged_data['EndTime'],
                    y=merged_data['predicted_response_time'],
                    mode='lines',
                    name='Przewidywany czas odpowiedzi (LSTM)',
                    line=dict(color=COLORS['predicted'], dash='dash')
                ))
        except Exception as e:
            print(f"Nie udało się dodać predykcji LSTM do wykresu: {e}")

    fig.update_layout(
        title='Czas odpowiedzi w czasie',
        xaxis_title='Czas',
        yaxis_title='Czas odpowiedzi (ms)',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font=dict(color=COLORS['text'])
    )

    return fig


def create_response_vs_users_graph(data, predictions=None):
    """Tworzy wykres zależności czasu odpowiedzi od liczby użytkowników."""
    fig = go.Figure()

    # Rzeczywiste dane
    fig.add_trace(go.Scatter(
        x=data['VusersNumber'],
        y=data['ResponseTime[ms]'],
        mode='markers',
        name='Rzeczywiste pomiary',
        marker=dict(color=COLORS['actual'])
    ))

    # Dodaj linię trendu dla rzeczywistych danych
    z = np.polyfit(data['VusersNumber'], data['ResponseTime[ms]'], 1)
    p = np.poly1d(z)
    x_trend = sorted(data['VusersNumber'].unique())
    fig.add_trace(go.Scatter(
        x=x_trend,
        y=p(x_trend),
        mode='lines',
        name='Trend rzeczywistych danych',
        line=dict(color=COLORS['actual'], dash='dot')
    ))

    # Dodaj predykcje jeśli są dostępne
    if predictions is not None and 'vusers' in predictions.columns and 'predicted_response_time' in predictions.columns:
        try:
            fig.add_trace(go.Scatter(
                x=predictions['vusers'],
                y=predictions['predicted_response_time'],
                mode='markers',
                name='Predykcje LSTM',
                marker=dict(color=COLORS['predicted'])
            ))

            # Dodaj linię trendu dla predykcji
            z_pred = np.polyfit(predictions['vusers'], predictions['predicted_response_time'], 1)
            p_pred = np.poly1d(z_pred)
            x_trend_pred = sorted(predictions['vusers'].unique())
            fig.add_trace(go.Scatter(
                x=x_trend_pred,
                y=p_pred(x_trend_pred),
                mode='lines',
                name='Trend predykcji LSTM',
                line=dict(color=COLORS['predicted'], dash='dot')
            ))
        except Exception as e:
            print(f"Nie udało się dodać linii trendu predykcji: {e}")

    fig.update_layout(
        title='Zależność czasu odpowiedzi od liczby użytkowników',
        xaxis_title='Liczba użytkowników',
        yaxis_title='Czas odpowiedzi (ms)',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font=dict(color=COLORS['text'])
    )

    return fig


def create_prediction_error_graph(predictions):
    """Tworzy wykres błędów predykcji LSTM."""
    if predictions is None or 'prediction_error' not in predictions.columns:
        # Pusta figura jeśli nie ma danych
        fig = go.Figure()
        fig.update_layout(
            title='Błąd predykcji LSTM (brak danych)',
            xaxis_title='Liczba użytkowników',
            yaxis_title='Błąd predykcji (ms)',
            plot_bgcolor=COLORS['background'],
            paper_bgcolor=COLORS['background'],
            font=dict(color=COLORS['text'])
        )
        return fig

    fig = go.Figure()

    # Wykres błędów predykcji
    fig.add_trace(go.Bar(
        x=predictions['vusers'],
        y=predictions['prediction_error'],
        name='Błąd predykcji',
        marker_color=predictions['prediction_error'].apply(
            lambda x: 'red' if x > 0 else 'green'
        )
    ))

    # Linia zerowa
    fig.add_shape(
        type="line",
        x0=min(predictions['vusers']),
        y0=0,
        x1=max(predictions['vusers']),
        y1=0,
        line=dict(color="black", width=2, dash="dash")
    )

    fig.update_layout(
        title='Błąd predykcji LSTM (Przewidywany - Rzeczywisty)',
        xaxis_title='Liczba użytkowników',
        yaxis_title='Błąd predykcji (ms)',
        plot_bgcolor=COLORS['background'],
        paper_bgcolor=COLORS['background'],
        font=dict(color=COLORS['text'])
    )

    return fig


# Definicja układu aplikacji
def serve_layout():
    """Generuje układ aplikacji Dash."""
    results_exist, predictions_exist = wait_for_files()

    if not results_exist:
        # Jeśli nie ma danych, wyświetl komunikat
        return dbc.Container([
            html.H1("Dashboard Monitoringu Wydajności", className="my-4"),
            dbc.Alert(
                "Oczekuję na dane wyników testów wydajnościowych. Odśwież stronę za kilka minut.",
                color="warning",
                className="my-4"
            ),
            dbc.Button("Odśwież", id="refresh-button", color="primary", className="my-2"),
            html.Div(id="refresh-trigger")
        ])

    # Wczytaj dane
    data, predictions = load_data()

    return dbc.Container([
        html.H1("Dashboard Monitoringu Wydajności", className="my-4"),

        dbc.Row([
            dbc.Col([
                html.H3("Kontrolki", className="mb-3"),
                dbc.Button("Odśwież dane", id="refresh-button", color="primary", className="mb-2 me-2"),
                dbc.Button("Automatyczne odświeżanie", id="auto-refresh", color="secondary", className="mb-2"),
                html.Div(id="refresh-status", className="text-muted mb-3"),
                dcc.Interval(id="interval-component", interval=15000, disabled=True),  # 15 sekund
                html.Div(id="refresh-trigger")
            ], width=12)
        ], className="mb-4"),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Aktywni użytkownicy w czasie"),
                    dbc.CardBody([
                        dcc.Graph(id="active-users-graph", figure=create_active_users_graph(data))
                    ])
                ])
            ], width=12, className="mb-4")
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Czas odpowiedzi w czasie"),
                    dbc.CardBody([
                        dcc.Graph(id="response-time-graph", figure=create_response_time_graph(data, predictions))
                    ])
                ])
            ], width=12, className="mb-4")
        ]),

        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Zależność czasu odpowiedzi od liczby użytkowników"),
                    dbc.CardBody([
                        dcc.Graph(id="response-vs-users-graph",
                                  figure=create_response_vs_users_graph(data, predictions))
                    ])
                ])
            ], width=12, className="mb-4")
        ]),

        # Wykresy błędów predykcji tylko jeśli są dane predykcji
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Błąd predykcji LSTM"),
                    dbc.CardBody([
                        dcc.Graph(
                            id="prediction-error-graph",
                            figure=create_prediction_error_graph(predictions)
                        ) if predictions_exist else html.Div("Brak danych predykcji LSTM.")
                    ])
                ])
            ], width=12, className="mb-4")
        ]) if predictions_exist else html.Div(),

        # Stopka z informacjami
        dbc.Row([
            dbc.Col([
                html.Hr(),
                html.P([
                    "Status danych: ",
                    html.Span(
                        f"Wyniki testów: {len(data)} rekordów" if data is not None else "Brak danych wyników",
                        className="badge bg-success me-2" if data is not None else "badge bg-danger me-2"
                    ),
                    html.Span(
                        f"Predykcje LSTM: {len(predictions)} rekordów" if predictions is not None else "Brak danych predykcji",
                        className="badge bg-success" if predictions is not None else "badge bg-warning"
                    )
                ])
            ], width=12)
        ])
    ], fluid=True)


app.layout = serve_layout


# Obsługa odświeżania
@app.callback(
    [Output("refresh-trigger", "children"),
     Output("refresh-status", "children"),
     Output("interval-component", "disabled")],
    [Input("refresh-button", "n_clicks"),
     Input("auto-refresh", "n_clicks"),
     Input("interval-component", "n_intervals")],
    [State("interval-component", "disabled")]
)
def handle_refresh(btn_click, auto_click, interval, is_disabled):
    ctx = callback_context
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'No clicks'

    # Odświeżanie z przycisku lub automatycznie
    now = pd.Timestamp.now().strftime("%H:%M:%S")

    if triggered_id == "auto-refresh":
        return "", f"Automatyczne odświeżanie {'wyłączone' if not is_disabled else 'włączone'} ({now})", not is_disabled

    if triggered_id in ["refresh-button", "interval-component"]:
        return "", f"Dane odświeżone o {now}", is_disabled

    return "", "Gotowy", is_disabled


# Aktualizacja wykresów po odświeżeniu
@app.callback(
    [Output("active-users-graph", "figure"),
     Output("response-time-graph", "figure"),
     Output("response-vs-users-graph", "figure"),
     Output("prediction-error-graph", "figure", allow_duplicate=True)],
    [Input("refresh-trigger", "children")],
    prevent_initial_call=True
)
def update_graphs(_):
    data, predictions = load_data()
    return (
        create_active_users_graph(data),
        create_response_time_graph(data, predictions),
        create_response_vs_users_graph(data, predictions),
        create_prediction_error_graph(predictions)
    )


# Uruchomienie serwera
if __name__ == "__main__":
    # Utworzenie katalogu results jeśli nie istnieje
    os.makedirs('src/results', exist_ok=True)
    print(f"Katalog results istnieje: {os.path.exists('src/results')}")

    # Wyraźne określenie interfejsu nasłuchiwania
    app.run_server(host="0.0.0.0", port=8050, debug=True)
