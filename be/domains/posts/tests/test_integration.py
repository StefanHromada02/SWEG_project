"""
Integration tests for end-to-end scenarios across the Post API.
"""
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from domains.posts.models import Post
from django.urls import reverse
from unittest.mock import patch
from io import BytesIO
from PIL import Image
import time


class PostAPIIntegrationTests(APITestCase):
    """End-to-end integration tests for complete workflows."""

    def setUp(self):
        self.list_url = reverse('post-list')
        self.user = User.objects.create_user(username='integration_user', password='test123')

    def create_test_image(self):
        """Helper to create a test image file."""
        file = BytesIO()
        image = Image.new('RGB', (100, 100), color='blue')
        image.save(file, 'JPEG')
        file.name = 'integration-test.jpg'
        file.seek(0)
        return file

    @patch('services.minio_storage.minio_storage.upload_image')
    @patch('services.minio_storage.minio_storage.delete_image')
    def test_complete_post_lifecycle(self, mock_delete, mock_upload):
        """Test complete lifecycle: create -> read -> update -> delete."""
        mock_upload.return_value = 'posts/lifecycle-test.jpg'
        mock_delete.return_value = True

        # 1. CREATE
        create_data = {
            'user': 1,
            'title': 'Lifecycle Test Post',
            'text': 'Initial content',
            'image_file': self.create_test_image()
        }
        create_response = self.client.post(self.list_url, create_data, format='multipart')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        post_id = create_response.data['id']
        self.assertEqual(create_response.data['image'], 'posts/lifecycle-test.jpg')

        # 2. READ
        detail_url = reverse('post-detail', kwargs={'pk': post_id})
        read_response = self.client.get(detail_url)
        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        self.assertEqual(read_response.data['title'], 'Lifecycle Test Post')

        # 3. UPDATE
        mock_upload.return_value = 'posts/updated-test.jpg'
        update_data = {
            'user': 1,
            'title': 'Updated Lifecycle Post',
            'text': 'Updated content',
            'image_file': self.create_test_image()
        }
        update_response = self.client.put(detail_url, update_data, format='multipart')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['title'], 'Updated Lifecycle Post')
        self.assertEqual(update_response.data['image'], 'posts/updated-test.jpg')

        # Verify old image was deleted
        mock_delete.assert_called_with('posts/lifecycle-test.jpg')

        # 4. DELETE
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify post is gone
        self.assertFalse(Post.objects.filter(pk=post_id).exists())
        
        # Verify final image was deleted
        self.assertEqual(mock_delete.call_count, 2)  # Once for update, once for delete

    def test_search_across_multiple_posts(self):
        """Test search functionality with multiple posts."""
        # Create multiple posts
        posts_data = [
            {'user': 1, 'title': 'Django Tutorial', 'text': 'Learn Django framework'},
            {'user': 2, 'title': 'Python Basics', 'text': 'Introduction to Python'},
            {'user': 1, 'title': 'REST API Design', 'text': 'Best practices for APIs'},
            {'user': 3, 'title': 'Django REST Framework', 'text': 'Advanced DRF concepts'},
        ]
        
        for data in posts_data:
            self.client.post(self.list_url, data, format='json')
        
        # Search for "Django"
        search_response = self.client.get(self.list_url, {'search': 'Django'})
        self.assertEqual(search_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(search_response.data), 2)
        
        # Search for "API"
        api_search = self.client.get(self.list_url, {'search': 'API'})
        self.assertEqual(len(api_search.data), 1)

    def test_ordering_with_pagination_scenario(self):
        """Test ordering works correctly with multiple posts."""
        # Create posts with known order
        for i in range(5):
            Post.objects.create(
                user=i + 1,
                title=f"Post {chr(65 + i)}",  # Post A, Post B, etc.
                text=f"Content {i}",
                image=""
            )
            time.sleep(0.01)  # Ensure different timestamps
        
        # Test ascending order by title
        asc_response = self.client.get(self.list_url, {'ordering': 'title'})
        titles = [post['title'] for post in asc_response.data]
        self.assertEqual(titles[0], 'Post A')
        self.assertEqual(titles[-1], 'Post E')
        
        # Test descending order by created_at
        desc_response = self.client.get(self.list_url, {'ordering': '-created_at'})
        self.assertEqual(desc_response.data[0]['title'], 'Post E')

    def test_bulk_operations_scenario(self):
        """Test creating and deleting multiple posts."""
        # Create multiple posts
        post_ids = []
        for i in range(3):
            data = {
                'user': 1,
                'title': f'Bulk Post {i}',
                'text': f'Bulk content {i}'
            }
            response = self.client.post(self.list_url, data, format='json')
            post_ids.append(response.data['id'])
        
        # Verify all were created
        list_response = self.client.get(self.list_url)
        self.assertGreaterEqual(len(list_response.data), 3)
        
        # Delete all posts
        for post_id in post_ids:
            detail_url = reverse('post-detail', kwargs={'pk': post_id})
            delete_response = self.client.delete(detail_url)
            self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify all are deleted
        for post_id in post_ids:
            self.assertFalse(Post.objects.filter(pk=post_id).exists())

    @patch('services.minio_storage.minio_storage.upload_image')
    def test_mixed_posts_with_and_without_images(self, mock_upload):
        """Test creating posts with and without images in same workflow."""
        mock_upload.return_value = 'posts/mixed-test.jpg'
        
        # Create post with image
        with_image = {
            'user': 1,
            'title': 'Post with Image',
            'text': 'Has image',
            'image_file': self.create_test_image()
        }
        response1 = self.client.post(self.list_url, with_image, format='multipart')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response1.data['image'], '')
        
        # Create post without image
        without_image = {
            'user': 2,
            'title': 'Post without Image',
            'text': 'No image'
        }
        response2 = self.client.post(self.list_url, without_image, format='json')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data['image'], '')
        
        # List all posts
        list_response = self.client.get(self.list_url)
        self.assertGreaterEqual(len(list_response.data), 2)

    def test_error_recovery_scenario(self):
        """Test that errors don't corrupt data."""
        # Create valid post
        valid_data = {
            'user': 1,
            'title': 'Valid Post',
            'text': 'Valid content'
        }
        valid_response = self.client.post(self.list_url, valid_data, format='json')
        self.assertEqual(valid_response.status_code, status.HTTP_201_CREATED)
        
        # Try to create invalid post
        invalid_data = {
            'user': 1,
            'text': 'Missing title'
        }
        invalid_response = self.client.post(self.list_url, invalid_data, format='json')
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Verify original post still exists and is retrievable
        detail_url = reverse('post-detail', kwargs={'pk': valid_response.data['id']})
        check_response = self.client.get(detail_url)
        self.assertEqual(check_response.status_code, status.HTTP_200_OK)
        self.assertEqual(check_response.data['title'], 'Valid Post')

    def test_concurrent_updates_scenario(self):
        """Test updating same post multiple times."""
        # Create initial post
        initial_data = {
            'user': 1,
            'title': 'Original Title',
            'text': 'Original content'
        }
        create_response = self.client.post(self.list_url, initial_data, format='json')
        post_id = create_response.data['id']
        detail_url = reverse('post-detail', kwargs={'pk': post_id})
        
        # Update 1
        update1 = {
            'user': 1,
            'title': 'Updated Title 1',
            'text': 'Updated content 1'
        }
        response1 = self.client.put(detail_url, update1, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Update 2
        update2 = {
            'user': 1,
            'title': 'Updated Title 2',
            'text': 'Updated content 2'
        }
        response2 = self.client.put(detail_url, update2, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Verify final state
        final_response = self.client.get(detail_url)
        self.assertEqual(final_response.data['title'], 'Updated Title 2')
        self.assertEqual(final_response.data['text'], 'Updated content 2')
