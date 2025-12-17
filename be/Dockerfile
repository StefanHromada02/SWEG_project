# Stage 1: Build-Umgebung
# Wird nur zum Installieren der Abhängigkeiten genutzt. Wir verwenden ein größeres Image.
FROM python:3.11-slim AS builder

# Setzt das Arbeitsverzeichnis
WORKDIR /app

# Kopiert die Konfigurationsdateien
# Da Sie VENV/pip verwenden, benötigen wir nur die requirements.txt
COPY requirements.txt .

# Installiert die Abhängigkeiten global im Builder-Image (nicht in venv)
# Wir installieren auch Pytest, pytest-cov und Flake8 für die Tests im CI-Lauf
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pytest pytest-cov flake8

# Stage 2: Laufzeit-Umgebung (Das finale, kleine Image)
# Wir wechseln zu einem noch kleineren Image für die Produktion/Tests, das die Abhängigkeiten von Stage 1 erbt.
FROM python:3.11-slim

# Setzt Umgebungsvariablen für Sicherheit und Konfiguration
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Erstellt einen Nicht-Root-Benutzer für Sicherheit
RUN adduser --disabled-password --gecos "" appuser
USER appuser
WORKDIR /home/appuser/app

# Kopiert die installierten Abhängigkeiten von der Builder-Stage
# Wir kopieren nur die Site-Packages, um das Image klein zu halten
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Kopiert die Python-Binaries, um Pytest/Flake8 direkt nutzen zu können
COPY --from=builder /usr/local/bin/pytest /usr/local/bin/flake8 /usr/local/bin/
# Wir müssen die Pfade des Benutzers aktualisieren, um die Binaries zu finden
ENV PATH="/usr/local/bin:$PATH"

# Kopiert den eigentlichen Anwendungscode
COPY --chown=appuser:appuser . .

# Wenn das Backend ein Webserver ist (z.B. mit FastAPI/Uvicorn):
# EXPOSE 8000
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]