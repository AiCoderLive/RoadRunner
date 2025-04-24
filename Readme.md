# RoadRunner - System Testowania i Przewidywania Wydajności

System RoadRunner służy do przeprowadzania testów wydajnościowych, analizowania wyników i przewidywania czasów odpowiedzi na podstawie modelu LSTM.

## Wymagania

- Docker i Docker Compose
- Git (do pobrania repozytorium)

## Struktura projektu

```
roadrunner/
├── data/               # Dane dla modeli
├── src/                # Kod źródłowy
│   ├── prediction_models/
│   │   ├── lstm/       # Model LSTM
│   │   │   ├── models/ # Zapisane modele LSTM
│   │   │   ├── LstmResponsePredictor.py
│   │   │   └── lstm_trainer.py  # Trening i punkt wejścia dla LSTM
│   │   ├── arima/      # Model ARIMA
│   │   ├── sarima/     # Model SARIMA
│   │   └── randomForestRegression/
│   ├── utils/          # Narzędzia pomocnicze
│   ├── visualization/  # Wizualizacja danych
│   ├── results/        # Wyniki testów
│   ├── Execute.py      # Skrypt do testów wydajnościowych
│   ├── init_directories.py  # Inicjalizacja katalogów
│   └── visualization_server.py  # Serwer wizualizacji
├── Dockerfile          # Definicja obrazu Docker
├── docker-compose.yml  # Konfiguracja usług Docker
├── docker-entrypoint.sh  # Skrypt startowy
├── requirements.txt    # Zależności Python
└── README.md           # Ten plik
```

## Uruchamianie systemu

### 1. Inicjalizacja projektu

Sklonuj repozytorium i przejdź do katalogu projektu:

```bash
git clone <adres-repozytorium>
cd roadrunner
```

### 2. Uruchomienie środowiska Docker

Aby uruchomić kompletne środowisko, wykonaj:

```bash
docker-compose up -d
```

To polecenie uruchomi trzy usługi:
- **visualizer** - Dashboard z wizualizacjami (dostępny na http://localhost:8050)
- **performance-test** - Wykonanie testów wydajnościowych
- **lstm-trainer** - Trenowanie modelu LSTM na podstawie wyników testów

### 3. Dostęp do dashboardu

Po uruchomieniu, dashboard z wizualizacjami będzie dostępny pod adresem:

```
http://localhost:8050
```

### 4. Zatrzymanie środowiska

Aby zatrzymać i usunąć kontenery:

```bash
docker-compose down
```

### 5. Uruchamianie poszczególnych usług

Można też uruchomić poszczególne usługi osobno:

```bash
# Tylko wizualizacja
docker-compose up -d visualizer

# Tylko testy wydajnościowe
docker-compose up -d performance-test

# Tylko trenowanie modelu
docker-compose up -d lstm-trainer
```

## Konfiguracja

### Parametry testów wydajnościowych

Parametry testów można modyfikować w pliku `docker-compose.yml` w sekcji `performance-test`:

```yaml
performance-test:
  environment:
    - MAX_TIMEOUT=20  # Maksymalny timeout dla zapytań (w sekundach)
```

### Parametry trenowania modelu LSTM

Parametry trenowania można modyfikować w pliku `src/lstm_trainer.py`.

## Rozwiązywanie problemów

### Logi

Aby sprawdzić logi konkretnej usługi:

```bash
docker-compose logs visualizer
docker-compose logs performance-test
docker-compose logs lstm-trainer
```

### Czyszczenie danych

Aby usunąć wszystkie dane i rozpocząć od nowa:

```bash
docker-compose down
rm -rf data/* models/* src/results/*
docker-compose up -d
```

## Rozszerzenie projektu

Projekt można łatwo rozszerzyć o dodatkowe modele i funkcje, dodając odpowiednie pliki w strukturze katalogów i aktualizując `docker-compose.yml`.
