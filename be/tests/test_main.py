"""
Tests for the main module and database operations.
"""

import pytest
import tempfile
import os
from sweg_project.database import DatabaseService
from sweg_project.models import User, Post, get_european_time
from zoneinfo import ZoneInfo
from datetime import datetime


class TestDatabaseService:
    """Test the DatabaseService class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        db_service = DatabaseService(f"sqlite:///{db_path}")
        yield db_service
        # Cleanup - close engine connections first
        db_service.engine.dispose()
        try:
            os.unlink(db_path)
        except PermissionError:
            # Windows sometimes holds locks on DB files, ignore cleanup errors in tests
            pass
    
    def test_create_user(self, temp_db):
        """Test user creation."""
        user = temp_db.create_user("testuser", "test@example.com")
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.created_at is not None
    
    def test_create_user_duplicate_username(self, temp_db):
        """Test that duplicate usernames raise an error."""
        temp_db.create_user("testuser", "test1@example.com")
        
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            temp_db.create_user("testuser", "test2@example.com")
    
    def test_get_user_by_username(self, temp_db):
        """Test retrieving user by username."""
        # Create user
        created_user = temp_db.create_user("findme", "findme@example.com")
        
        # Find user
        found_user = temp_db.get_user_by_username("findme")
        
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "findme"
        assert found_user.email == "findme@example.com"
    
    def test_get_user_by_username_not_found(self, temp_db):
        """Test retrieving non-existent user."""
        user = temp_db.get_user_by_username("nonexistent")
        assert user is None
    
    def test_create_post(self, temp_db):
        """Test post creation."""
        # First create a user
        user = temp_db.create_user("postuser", "postuser@example.com")
        
        # Create post
        post = temp_db.create_post(
            title="Test Post",
            text="This is a test post content.",
            user_id=user.id,
            image="https://example.com/test.jpg"
        )
        
        assert post.id is not None
        assert post.title == "Test Post"
        assert post.text == "This is a test post content."
        assert post.user_id == user.id
        assert post.image == "https://example.com/test.jpg"
        assert post.created_at is not None
    
    def test_create_post_without_image(self, temp_db):
        """Test post creation without image."""
        user = temp_db.create_user("imageuser", "imageuser@example.com")
        
        post = temp_db.create_post(
            title="No Image Post",
            text="This post has no image.",
            user_id=user.id
        )
        
        assert post.image is None
    
    def test_get_latest_post(self, temp_db):
        """Test retrieving the latest post."""
        user = temp_db.create_user("latestuser", "latest@example.com")
        
        # Create multiple posts
        post1 = temp_db.create_post("First Post", "First content", user.id)
        post2 = temp_db.create_post("Second Post", "Second content", user.id)
        post3 = temp_db.create_post("Latest Post", "Latest content", user.id)
        
        latest = temp_db.get_latest_post()
        
        assert latest is not None
        assert latest.title == "Latest Post"
        assert latest.text == "Latest content"
        assert latest.user.username == "latestuser"  # Test relationship loading
    
    def test_get_latest_post_empty_db(self, temp_db):
        """Test retrieving latest post from empty database."""
        latest = temp_db.get_latest_post()
        assert latest is None
    
    def test_get_all_posts(self, temp_db):
        """Test retrieving all posts."""
        user = temp_db.create_user("alluser", "all@example.com")
        
        # Create posts
        post1 = temp_db.create_post("Post 1", "Content 1", user.id)
        post2 = temp_db.create_post("Post 2", "Content 2", user.id)
        post3 = temp_db.create_post("Post 3", "Content 3", user.id)
        
        all_posts = temp_db.get_all_posts()
        
        assert len(all_posts) == 3
        # Should be ordered by created_at desc (newest first)
        assert all_posts[0].title == "Post 3"
        assert all_posts[1].title == "Post 2"
        assert all_posts[2].title == "Post 1"
    
    def test_get_posts_by_user(self, temp_db):
        """Test retrieving posts by specific user."""
        user1 = temp_db.create_user("user1", "user1@example.com")
        user2 = temp_db.create_user("user2", "user2@example.com")
        
        # Create posts for both users
        post1 = temp_db.create_post("User1 Post1", "Content", user1.id)
        post2 = temp_db.create_post("User2 Post1", "Content", user2.id)
        post3 = temp_db.create_post("User1 Post2", "Content", user1.id)
        
        user1_posts = temp_db.get_posts_by_user(user1.id)
        user2_posts = temp_db.get_posts_by_user(user2.id)
        
        assert len(user1_posts) == 2
        assert len(user2_posts) == 1
        assert all(post.user_id == user1.id for post in user1_posts)
        assert all(post.user_id == user2.id for post in user2_posts)


class TestModels:
    """Test the database models."""
    
    def test_get_european_time(self):
        """Test that european time function returns correct timezone."""
        eu_time = get_european_time()
        
        assert eu_time.tzinfo is not None
        assert str(eu_time.tzinfo) in ["Europe/Berlin", "+01:00", "+02:00"]  # Handle DST
        
        # Should be roughly current time
        now_utc = datetime.now(ZoneInfo("UTC"))
        time_diff = abs((eu_time - now_utc).total_seconds())
        assert time_diff < 7200  # Should be within 2 hours (accounting for timezone difference)
    
    def test_user_repr(self):
        """Test User string representation."""
        user = User(id=1, username="testuser", email="test@example.com")
        expected = "<User(id=1, username='testuser')>"
        assert repr(user) == expected
    
    def test_post_repr(self):
        """Test Post string representation."""
        post = Post(id=1, title="Test Post", text="Content", user_id=5)
        expected = "<Post(id=1, title='Test Post', user_id=5)>"
        assert repr(post) == expected


class TestIntegration:
    """Integration tests for the full workflow."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        db_service = DatabaseService(f"sqlite:///{db_path}")
        yield db_service
        # Cleanup - close engine connections first
        db_service.engine.dispose()
        try:
            os.unlink(db_path)
        except PermissionError:
            # Windows sometimes holds locks on DB files, ignore cleanup errors in tests
            pass
    
    def test_full_workflow(self, temp_db):
        """Test a complete user and post creation workflow."""
        # Create user
        user = temp_db.create_user("workflow_user", "workflow@example.com")
        
        # Create posts
        post1 = temp_db.create_post("First", "First post content", user.id)
        post2 = temp_db.create_post("Second", "Second post content", user.id, "image.jpg")
        
        # Verify user can be found
        found_user = temp_db.get_user_by_username("workflow_user")
        assert found_user.id == user.id
        
        # Verify latest post
        latest = temp_db.get_latest_post()
        assert latest.title == "Second"
        assert latest.user.username == "workflow_user"
        
        # Verify all posts
        all_posts = temp_db.get_all_posts()
        assert len(all_posts) == 2
        
        # Verify user's posts
        user_posts = temp_db.get_posts_by_user(user.id)
        assert len(user_posts) == 2