from django.test import TestCase
from django.contrib.auth.models import User
from domains.posts.serializers import PostSerializer


class PostSerializerTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='serializer_user', password='password123')

        cls.valid_data = {
            "title": "Ein valider Titel",
            "text": "Ein valider Textinhalt.",
            "image": "http://example.com/valid.jpg"
        }

        cls.invalid_data_no_title = {
            "text": "Hier fehlt der Titel.",
            "image": "http://example.com/invalid.jpg"
        }

    def test_serializer_with_valid_data(self):
        """Testet die Deserialisierung (Validierung) von korrekten Daten."""
        serializer = PostSerializer(data=self.valid_data)

        # Überprüft, ob der Serializer die Daten als gültig erkennt
        is_valid = serializer.is_valid()

        # Zeige Fehler an, falls ungültig (hilfreich beim Debuggen)
        if not is_valid:
            print(serializer.errors)

        self.assertTrue(is_valid)

    def test_serializer_with_invalid_data_missing_title(self):
        """Testet, ob der Serializer fehlende Pflichtfelder (z.B. title) erkennt."""
        serializer = PostSerializer(data=self.invalid_data_no_title)

        self.assertFalse(serializer.is_valid())
        # Stellt sicher, dass der Fehler 'title' als Ursache nennt
        self.assertIn('title', serializer.errors)