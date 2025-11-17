from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from domains.posts.models import Post
from django.urls import reverse
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image
import time


class PostViewSetTests(APITestCase):
    """Tests for basic CRUD operations."""

    @classmethod
    def setUpTestData(cls):
        # Erstelle einen Testbenutzer
        cls.user = User.objects.create_user(username='api_user', password='password123')

        # Erstelle einen Test-Post
        cls.post = Post.objects.create(
            user=cls.user,
            title="API Test Post",
            text="Inhalt für den API Test.",
            image="posts/test.jpg"
        )

    def setUp(self):
        # URLs werden in setUp definiert, da sie instance-specific sein können
        self.list_url = reverse('post-list') # 'post-list' ist der List- und Create-Endpunkt deiner ViewSet-Route → entspricht zB /api/posts/
        self.detail_url = reverse('post-detail', kwargs={'pk': self.post.pk}) # 'post-detail' ist der Detail-, Update- und Delete-Endpunkt → entspricht zB /api/posts/<id>/

    def test_get_post_list(self):
        """Test GET /api/posts/ returns list of posts."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_get_post_detail(self):
        """Test GET /api/posts/<pk>/ returns single post."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "API Test Post")

    def test_create_post_without_image(self):
        """Test POST /api/posts/ creates post without image."""
        data = {
            "user": self.user.id,
            "title": "Neuer Post",
            "text": "Testinhalt"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], "Neuer Post")
        self.assertEqual(response.data['image'], "")

    def test_create_post_invalid_data(self):
        """Test POST /api/posts/ with missing required fields."""
        data = {
            "text": "Hier fehlt der Titel"
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_update_post(self):
        """Test PUT /api/posts/<pk>/ updates post."""
        data = {
            "user": 1,
            "title": "Updated Title",
            "text": "Updated content"
        }
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Updated Title")
        
        # Verify in database
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Updated Title")

    def test_partial_update_post(self):
        """Test PATCH /api/posts/<pk>/ partially updates post."""
        data = {"title": "Partially Updated"}
        response = self.client.patch(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Partially Updated")
        
        # Verify text remained unchanged
        self.assertEqual(response.data['text'], "Inhalt für den API Test.")

    @patch('services.minio_storage.minio_storage.delete_image')
    def test_delete_post(self, mock_delete):
        """Test DELETE /api/posts/<pk>/ deletes post and calls MinIO delete."""
        mock_delete.return_value = True
        
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())
        
        # Verify MinIO delete was called
        mock_delete.assert_called_once_with("posts/test.jpg")

    def test_get_nonexistent_post(self):
        """Test GET /api/posts/999/ returns 404."""
        url = reverse('post-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PostSearchFilterTests(APITestCase):
    """Tests for search and filter functionality."""

    @classmethod
    def setUpTestData(cls):
        # Create test users
        cls.user1 = User.objects.create_user(username='user1', password='pass123')
        cls.user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Create test posts with different content
        cls.post1 = Post.objects.create(
            user=cls.user1,
            title="Django REST Framework Tutorial",
            text="Learn how to build REST APIs",
            image=""
        )
        time.sleep(0.01)  # Ensure different timestamps
        cls.post2 = Post.objects.create(
            user=cls.user2,
            title="Python Programming Guide",
            text="Complete guide to Python",
            image=""
        )
        time.sleep(0.01)
        cls.post3 = Post.objects.create(
            user=cls.user1,
            title="Docker Containers",
            text="Learn Docker and containerization",
            image=""
        )

    def setUp(self):
        self.list_url = reverse('post-list')

    def test_search_by_title(self):
        """Test search parameter finds posts by title."""
        response = self.client.get(self.list_url, {'search': 'Django'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('Django', response.data[0]['title'])

    def test_search_by_text(self):
        """Test search parameter finds posts by text content."""
        response = self.client.get(self.list_url, {'search': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('Python', response.data[0]['title'])

    def test_search_case_insensitive(self):
        """Test search is case-insensitive."""
        response = self.client.get(self.list_url, {'search': 'docker'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIn('Docker', response.data[0]['title'])

    def test_search_no_results(self):
        """Test search with no matches returns empty list."""
        response = self.client.get(self.list_url, {'search': 'NonExistentTerm'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_ordering_by_title_asc(self):
        """Test ordering by title ascending."""
        response = self.client.get(self.list_url, {'ordering': 'title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [post['title'] for post in response.data]
        self.assertEqual(titles, sorted(titles))

    def test_ordering_by_title_desc(self):
        """Test ordering by title descending."""
        response = self.client.get(self.list_url, {'ordering': '-title'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [post['title'] for post in response.data]
        self.assertEqual(titles, sorted(titles, reverse=True))

    def test_ordering_by_created_at_desc(self):
        """Test ordering by created_at (newest first)."""
        response = self.client.get(self.list_url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Newest (post3) should be first
        self.assertEqual(response.data[0]['id'], self.post3.id)

    def test_ordering_by_created_at_asc(self):
        """Test ordering by created_at (oldest first)."""
        response = self.client.get(self.list_url, {'ordering': 'created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Oldest (post1) should be first
        self.assertEqual(response.data[0]['id'], self.post1.id)

    def test_combined_search_and_ordering(self):
        """Test combining search and ordering parameters."""
        response = self.client.get(self.list_url, {
            'search': 'guide',
            'ordering': 'title'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should find posts with 'guide' in title or text
        self.assertGreaterEqual(len(response.data), 1)


class PostImageUploadTests(APITestCase):
    """Tests for image upload functionality with MinIO."""

    def setUp(self):
        self.list_url = reverse('post-list')

    def create_test_image(self):
        """Helper to create a test image file."""
        file = BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file, 'JPEG')
        file.name = 'test.jpg'
        file.seek(0)
        return file

    @patch('services.minio_storage.minio_storage.upload_image')
    def test_create_post_with_image_upload(self, mock_upload):
        """Test POST with image_file uploads to MinIO."""
        mock_upload.return_value = 'posts/uuid-test.jpg'
        
        image_file = self.create_test_image()
        data = {
            'user': 1,
            'title': 'Post with Image',
            'text': 'Test content',
            'image_file': image_file
        }
        
        response = self.client.post(self.list_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['image'], 'posts/uuid-test.jpg')
        mock_upload.assert_called_once()

    @patch('services.minio_storage.minio_storage.upload_image')
    def test_upload_image_failure_handling(self, mock_upload):
        """Test that upload failure is handled gracefully."""
        mock_upload.return_value = None  # Simulate upload failure
        
        image_file = self.create_test_image()
        data = {
            'user': 1,
            'title': 'Failed Upload',
            'text': 'Test',
            'image_file': image_file
        }
        
        response = self.client.post(self.list_url, data, format='multipart')
        
        # Should return 400 Bad Request due to ValidationError
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('image_file', response.data)

    @patch('services.minio_storage.minio_storage.upload_image')
    @patch('services.minio_storage.minio_storage.delete_image')
    def test_update_post_replaces_image(self, mock_delete, mock_upload):
        """Test PUT with new image deletes old and uploads new."""
        # Create post with existing image
        post = Post.objects.create(
            user=self.user,
            title="Original",
            text="Text",
            image="posts/old-image.jpg"
        )
        
        mock_upload.return_value = 'posts/new-image.jpg'
        mock_delete.return_value = True
        
        detail_url = reverse('post-detail', kwargs={'pk': post.pk})
        image_file = self.create_test_image()
        data = {
            'user': 1,
            'title': 'Updated',
            'text': 'Updated text',
            'image_file': image_file
        }
        
        response = self.client.put(detail_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['image'], 'posts/new-image.jpg')
        
        # Verify old image was deleted
        mock_delete.assert_called_once_with('posts/old-image.jpg')
        mock_upload.assert_called_once()


class PostCustomActionsTests(APITestCase):
    """Tests for custom ViewSet actions."""

    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='action_user1', password='pass123')
        cls.user2 = User.objects.create_user(username='action_user2', password='pass123')
        cls.post1 = Post.objects.create(user=cls.user1, title="Post 1", text="Text 1")
        cls.post2 = Post.objects.create(user=cls.user2, title="Post 2", text="Text 2")

    def test_my_posts_action(self):
        """Test custom my_posts action endpoint."""
        url = reverse('post-my-posts')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        # Currently returns all posts (no user filtering implemented)
        self.assertGreaterEqual(len(response.data), 2)