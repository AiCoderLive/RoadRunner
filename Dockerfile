FROM python:3.9-slim

# Zainstaluj potrzebne pakiety systemowe
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj pliki wymagań i zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod źródłowy aplikacji
COPY . .

# Upewnij się, że istnieje katalog na wyniki
RUN mkdir -p /app/src/results