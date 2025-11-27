from django.test import TestCase

from domains.users.models import User
from domains.posts.models import Post


class PostSimpleTest(TestCase):
    def test_create_post(self):
        # Arrange: create a simple user
        user = User.objects.create(
            name="Alice",
            email="alice@technikum-wien.at",
            study_program="Software Engineering",
        )

        # Act: create a post for that user
        post = Post.objects.create(
            user=user,
            title="Hello World",
            text="This is my first post!",
            image="https://example.com/image.jpg",
        )

        # Assert: basic invariants
        self.assertIsNotNone(post.id)
        self.assertEqual(post.user, user)
        self.assertEqual(str(post), "Hello World by Alice")
