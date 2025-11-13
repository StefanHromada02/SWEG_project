#!/bin/sh

# Stellt sicher, dass das Skript bei jedem Fehler sofort abbricht
set -e

# Erhalte die DB-Variablen aus der Docker-Umgebung
# (Stellen Sie sicher, dass sie in docker-compose.yml im 'backend' environment definiert sind)
DB_HOST=${POSTGRES_HOST:-db}
DB_PORT=${POSTGRES_PORT:-5432}
DB_USER=${POSTGRES_USER:-postgres}
DB_NAME=${POSTGRES_DB:-social_media_db}
# HINWEIS: Das Passwort wird aus Sicherheitsgründen oft über PGPASSWORD übergeben

echo "Warte auf die PostgreSQL-Datenbank unter $DB_HOST:$DB_PORT..."

# Python-Skript zum Warten auf die DB
# Wir verwenden 'until' anstelle von 'while'
until python -c "import sys, os, psycopg2
try:
    conn = psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD'),
        host=os.environ.get('POSTGRES_HOST'),
        port=os.environ.get('POSTGRES_PORT')
    )
    conn.close()
except psycopg2.OperationalError as e:
    print(f'Datenbank ist nicht bereit: {e}')
    sys.exit(1)
print('Datenbank ist bereit!')
"
do
  sleep 2
done

# 1. Erstelle die Migrationsdateien (Bauplan), falls sie fehlen
echo "Erstelle Migrationsdateien (falls nötig)..."
python manage.py makemigrations posts

# 2. Wende Datenbank-Migrationen an (erstellt die Tabellen)
echo "Wende Datenbank-Migrationen an..."
python manage.py migrate --noinput

# 3. Starte den Django-Server
echo "Starte Django-Server..."
exec "$@"