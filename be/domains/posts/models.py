from django.db import models
from django.contrib.auth.models import User
from .managers import PostManager # Importiere den neuen Manager

class Post(models.Model):
    user = models.IntegerField()
    title = models.CharField(max_length=200)
    text = models.TextField()
    image = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = PostManager()

    def __str__(self):
        # Get user object to display username
        try:
            user_obj = User.objects.get(id=self.user)
            return f"{self.title} by {user_obj.username}"
        except User.DoesNotExist:
            return f"{self.title} by user#{self.user}"