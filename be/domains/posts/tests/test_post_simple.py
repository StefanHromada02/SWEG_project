from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from domains.users.models import User
from domains.posts.models import Post


class PostSimpleTest(SimpleTestCase):

    @patch("domains.posts.models.Post.objects.create")
    @patch("domains.users.models.User.objects.create")
    def test_create_post(self, mock_create_user, mock_create_post):
        # Arrange – Fake User
        fake_user = User(
            id=1,
            name="Alice",
            email="alice@technikum-wien.at",
            study_program="Software Engineering",
        )
        mock_create_user.return_value = fake_user

        # Arrange – Fake Post
        fake_post = Post(
            id=1,
            user=fake_user,
            title="Hello World",
            text="This is my first post!",
            image="https://example.com/image.jpg",
        )
        mock_create_post.return_value = fake_post

        # Act
        user = User.objects.create(
            name="Alice",
            email="alice@technikum-wien.at",
            study_program="Software Engineering",
        )
        post = Post.objects.create(
            user=user,
            title="Hello World",
            text="This is my first post!",
            image="https://example.com/image.jpg",
        )

        # Assert
        self.assertEqual(post.id, 1)
        self.assertEqual(post.user.name, "Alice")
        self.assertEqual(str(post), "Hello World by Alice")

        mock_create_user.assert_called_once()
        mock_create_post.assert_called_once()
        self.assertEqual(str(post), "Hello World by Alice")