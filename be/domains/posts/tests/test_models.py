from django.test import TestCase
from django.contrib.auth.models import User
from domains.posts.models import Post
from django.utils import timezone
import time


class PostModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Setup data that will be used by all test methods
        cls.user = User.objects.create_user(username='testuser', password='password123')

        # Create posts with controlled timing for sorting tests
        cls.post_older = Post.objects.create(
            user=cls.user.id,
            title="Older Post",
            text="This is an older post.",
            image="http://example.com/older.jpg"
        )
        # Ensure the next post is measurably newer
        time.sleep(0.01)
        cls.post_newer = Post.objects.create(
            user=cls.user.id,
            title="Newer Post",
            text="This is a newer post.",
            image="http://example.com/newer.jpg"
        )

    def test_post_str_representation(self):
        """Testet die __str__ Methode des Post-Modells."""
        expected_str = f"{self.post_older.title} by user#{self.user.id}"
        self.assertEqual(str(self.post_older), expected_str)

    def test_manager_newest_first(self):
        """Testet, ob der PostManager die Posts korrekt sortiert."""
        # Ruft die QuerySet-Methode über den Manager auf
        posts = Post.objects.newest_first()

        self.assertEqual(posts.first(), self.post_newer, "Der neueste Post sollte an erster Stelle stehen.")
        self.assertEqual(posts.last(), self.post_older, "Der älteste Post sollte an letzter Stelle stehen.")

    def test_manager_with_author_prefetching(self):
        """Testet, ob 'with_author' die Posts zurückgibt."""
        # Since user is IntegerField, with_author just returns posts
        posts = list(Post.objects.with_author())
        
        # Verify we get all posts
        self.assertEqual(len(posts), 2)
        
        # Verify posts have user IDs
        for post in posts:
            self.assertIsNotNone(post.user)
            self.assertIsInstance(post.user, int)