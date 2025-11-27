from django.db import models
from django.db.models import QuerySet


class UserQuerySet(QuerySet):
    """QuerySet methods for User model, to enable chaining."""

    def by_study_program(self, program):
        """Filter users by study program."""
        return self.filter(study_program__iexact=program)

    def newest_first(self):
        """Orders users by creation date, newest first."""
        return self.order_by('-created_at')


class UserManager(models.Manager):
    """Custom Manager that uses the custom QuerySet."""
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)
    
    def by_study_program(self, program):
        """Filter users by study program."""
        return self.get_queryset().by_study_program(program)
    
    def newest_first(self):
        """Orders users by creation date, newest first."""
        return self.get_queryset().newest_first()
