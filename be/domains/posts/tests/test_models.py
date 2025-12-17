import pytest
from domains.posts.models import Post
from domains.users.models import User
import time


@pytest.mark.django_db
class TestPostModel:
    """Tests for Post model."""

    def test_post_creation(self):
        """Test creating a post."""
        user = User.objects.create(
            name="Test User",
            email="test@technikum-wien.at",
            study_program="Software Engineering"
        )
        post = Post.objects.create(
            user=user,
            title="Test Post",
            text="This is a test post.",
            image="posts/test.jpg"
        )
        
        assert post.id is not None
        assert post.title == "Test Post"
        assert post.user == user
        assert str(post) == "Test Post by Test User"

    def test_manager_newest_first(self):
        """Test that PostManager returns posts sorted by newest first."""
        user = User.objects.create(
            name="Test User",
            email="test@technikum-wien.at",
            study_program="Software Engineering"
        )
        
        post_older = Post.objects.create(
            user=user,
            title="Older Post",
            text="This is an older post.",
            image=""
        )
        time.sleep(0.01)
        post_newer = Post.objects.create(
            user=user,
            title="Newer Post",
            text="This is a newer post.",
            image=""
        )
        
        posts = Post.objects.newest_first()
        assert posts.first() == post_newer
        assert posts.last() == post_older