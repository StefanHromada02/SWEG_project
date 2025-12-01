from django.db import models
from django.contrib.postgres.fields import ArrayField
from .managers import UserManager


class User(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True, help_text="Must end with @technikum-wien.at")
    study_program = models.CharField(max_length=200)
    interests = ArrayField(
        models.CharField(max_length=100),
        size=5,
        blank=True,
        default=list,
        help_text="List of interests, max 5"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    def __str__(self):
        return f"{self.name} ({self.study_program})"
