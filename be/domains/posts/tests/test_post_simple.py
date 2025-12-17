import pytest
from unittest.mock import patch
from domains.users.models import User
from domains.posts.models import Post


class TestPostSimple:
    """Simple unit tests for Post model."""

    @patch("domains.posts.models.Post.objects.create")
    @patch("domains.users.models.User.objects.create")
    def test_create_post_mocked(self, mock_create_user, mock_create_post):
        """Test creating a post with mocked database."""
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
        assert post.id == 1
        assert post.user.name == "Alice"
        assert str(post) == "Hello World by Alice"
        assert mock_create_user.call_count == 1
        assert mock_create_post.call_count == 1