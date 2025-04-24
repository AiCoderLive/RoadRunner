#!/bin/bash
set -e

# Funkcja do wyświetlania komunikatów z timestampem
log() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*"
}

# Inicjalizacja katalogów projektu
log "Inicjalizacja katalogów..."
python -u src/init_directories.py

# Sprawdź typ uruchamianego serwisu
case "$1" in
  "performance-test")
    log "Uruchamianie testów wydajnościowych..."
    exec python -u src/Execute.py "$@"
    ;;

  "lstm-trainer")
    log "Uruchamianie trenowania modelu LSTM..."
    # Upewnij się, że katalog na modele LSTM istnieje
    mkdir -p src/prediction_models/lstm/models
    exec python -u src/prediction_models/lstm/lstm_trainer.py "$@"
    ;;

  "visualizer")
    log "Uruchamianie serwera wizualizacji..."
    exec python -u src/visualization_server.py "$@"
    ;;

  *)
    # Jeśli podano własną komendę, wykonaj ją
    if [ -n "$1" ]; then
      log "Wykonywanie komendy: $*"
      exec "$@"
    else
      log "Nie określono typu serwisu. Dostępne opcje: performance-test, lstm-trainer, visualizer"
      exit 1
    fi
    ;;
esac