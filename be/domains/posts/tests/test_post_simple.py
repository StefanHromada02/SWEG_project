from django.test import TestCase
from django.utils import timezone

from domains.users.models import User
from domains.posts.models import Post


class PostSimpleTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name="Alice",
            email="alice@technikum-wien.at",
            study_program="Software Engineering",
            interests=[],
            created_at=timezone.now(),
        )

    def test_create_post(self):
        post = Post.objects.create(
            user=self.user,
            title="Hello World",
            text="This is my first post!",
            image="https://example.com/image.jpg",
        )

        self.assertIsNotNone(post.id)
        self.assertEqual(post.user, self.user)
        self.assertEqual(str(post), "Hello World by Alice")