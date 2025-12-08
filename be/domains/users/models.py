from django.db import models
from django.contrib.postgres.fields import ArrayField
from .managers import UserManager


class User(models.Model):
    # Keycloak user identifier - primary link to Keycloak
    keycloak_id = models.CharField(max_length=255, unique=True, db_index=True, help_text="Keycloak user ID (sub claim)")
    username = models.CharField(max_length=200, unique=True, help_text="Keycloak username")
    
    # User profile information
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True, help_text="Must end with @technikum-wien.at")
    study_program = models.CharField(max_length=200, blank=True, default="")
    interests = ArrayField(
        models.CharField(max_length=100),
        size=5,
        blank=True,
        default=list,
        help_text="List of interests, max 5"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=['keycloak_id']),
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.name} ({self.study_program})"
