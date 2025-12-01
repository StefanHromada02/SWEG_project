from django.db import models
from .managers import CommentManager


class Comment(models.Model):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        'posts.Post',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CommentManager()

    class Meta:
        ordering = ['-created_at']  # Newest first by default

    def __str__(self):
        return f"Comment by {self.user.name} on {self.post.title}"
