FROM python:3.10-slim

WORKDIR /app

# Kopiowanie plików projektu
COPY requirements.txt .
COPY src/ ./src/

# Instalacja zależności
RUN pip install --no-cache-dir -r requirements.txt

# Utworzenie katalogu na wyniki jeśli nie istnieje
RUN mkdir -p src/results

# Katalog na modele
RUN mkdir -p model

# Zmienne środowiskowe
ENV PYTHONPATH=/app

# Port dla Dash
EXPOSE 8050

# Domyślne uruchomienie - monitoring
CMD ["python", "./src/monitoring.py", "./src/results/results.csv", "--use_interval"]