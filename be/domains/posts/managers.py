# posts/managers.py
from django.db import models
from django.db.models import QuerySet

class PostQuerySet(QuerySet):
    """QuerySet methods for Post model, to enable chaining."""

    def with_author(self):
        """Returns queryset (user is IntegerField, not ForeignKey)."""
        # Since user is IntegerField, we can't use select_related
        return self

    def newest_first(self):
        """Orders posts by creation date, newest first."""
        # Das Minuszeichen '-' bewirkt die absteigende Sortierung (desc)
        return self.order_by('-created_at')

class PostManager(models.Manager):
    """Custom Manager that uses the custom QuerySet."""
    def get_queryset(self):
        return PostQuerySet(self.model, using=self._db)
    
    def with_author(self):
        """Delegate to QuerySet method."""
        return self.get_queryset().with_author()
    
    def newest_first(self):
        """Delegate to QuerySet method."""
        return self.get_queryset().newest_first()
