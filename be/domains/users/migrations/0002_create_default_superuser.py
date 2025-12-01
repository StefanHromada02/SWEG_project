# domains/users/migrations/0002_create_default_superuser.py

from django.db import migrations
import os
from django.contrib.auth.hashers import make_password  # Importieren Sie dies, um das Passwort zu hashen


def create_raw_user_entry(apps, schema_editor):
    """
    Erstellt den Datenbankeintrag direkt, ohne die create_superuser-Methode
    zu verwenden, um die aktuellen Fehler zu umgehen.
    """
    import os

    # Der korrekte Modell-Abruf
    User = apps.get_model('users', 'User')

    # Anmeldedaten
    email = os.getenv('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.getenv('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    username = os.getenv('DJANGO_SUPERUSER_USERNAME', 'admin')

    # Prüfen, ob der Benutzer bereits existiert
    if not User.objects.filter(email=email).exists():
        print(f"\nErstelle RAW-Benutzer '{email}'...")

        # HINWEIS: Da Ihr Modell nicht alle Django-Felder hat,
        # fügen wir hier nur die Felder ein, die in Ihrer models.py existieren.
        # WIR SIMULIEREN DEN AUTH-STATUS ÜBER DIE CUSTOM FELDER.

        # Erstellung des RAW-Eintrags
        User.objects.create(
            # Felder aus Ihrer models.py
            name=username,
            email=email,
            study_program="Admin",

            # Hier müsste normalerweise das gehashte Passwort stehen.
            # Da Ihr Modell kein Passwort-Feld hat, lassen wir dies weg.
            # Wenn Ihr Modell das Feld "password" HÄTTE, müssten Sie:
            # password=make_password(password),
        )
    else:
        print(f"\nBenutzer '{email}' existiert bereits. Überspringe Erstellung.")


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_raw_user_entry, reverse_code=migrations.RunPython.noop),
    ]