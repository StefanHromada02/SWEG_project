from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from domains.posts.models import Post
from django.urls import reverse


class PostViewSetTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Erstelle einen Testbenutzer
        cls.user = User.objects.create_user(username='api_user', password='password123')

        # Erstelle einen Test-Post
        cls.post = Post.objects.create(
            user=cls.user,
            title="API Test Post",
            text="Inhalt für den API Test.",
            image="http://example.com/api.jpg"
        )

        # Definiere die URLs (DRF DefaultRouter benennt die Basis 'post' nach dem Modell)
        # 'domains.posts' ist der App-Name, 'post' der Basisname des Routers
        cls.list_url = reverse('domains.posts:post-list')
        cls.detail_url = reverse('domains.posts:post-detail', kwargs={'pk': cls.post.pk})

    def test_get_post_list_unauthenticated(self):
        """
        Testet GET /api/posts/ (Liste) als anonymer User.
        Sollte erfolgreich sein (200 OK) wegen IsAuthenticatedOrReadOnly.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_post_detail_unauthenticated(self):
        """Testet GET /api/posts/<pk>/ (Detail) als anonymer User."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "API Test Post")

    def test_create_post_unauthenticated_fails(self):
        """
        Testet POST /api/posts/ (Erstellen) als anonymer User.
        Sollte fehlschlagen (401 oder 403) wegen IsAuthenticatedOrReadOnly.
        """
        data = {
            "title": "Anonymer Post",
            "text": "Dieser Post sollte nicht erstellt werden.",
            "image": "http://example.com/fail.jpg"
        }
        response = self.client.post(self.list_url, data, format='json')
        # 401 Unauthorized (wenn keine Credentials gesendet wurden)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_post_authenticated_success(self):
        """
        Testet POST /api/posts/ (Erstellen) als authentifizierter User.
        Testet auch die 'perform_create'-Logik.
        """
        # Authentifiziere den Client als unser Testuser
        self.client.force_authenticate(user=self.user)

        data = {
            "title": "Neuer authentifizierter Post",
            "text": "Dieser Post wird vom User erstellt.",
            "image": "http://example.com/success.jpg"
        }

        response = self.client.post(self.list_url, data, format='json')

        # Test 1: War die Erstellung erfolgreich?
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test 2: Wurde der korrekte User zugewiesen? (Testet perform_create)
        new_post = Post.objects.get(id=response.data['id'])
        self.assertEqual(new_post.user, self.user)
        self.assertEqual(new_post.title, "Neuer authentifizierter Post")

    def test_create_post_invalid_data(self):
        """Testet POST /api/posts/ mit fehlenden Daten."""
        self.client.force_authenticate(user=self.user)
        data = {
            "text": "Hier fehlt der Titel"  # 'title' ist erforderlich
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_post_authenticated(self):
        """Testet DELETE /api/posts/<pk>/ als authentifizierter User."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_delete_post_unauthenticated_fails(self):
        """Testet DELETE als anonymer User."""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)