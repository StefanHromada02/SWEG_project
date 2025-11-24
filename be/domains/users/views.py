from rest_framework import viewsets, filters
from drf_spectacular.utils import extend_schema

from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users.
    
    Provides CRUD operations and search functionality for users.
    """
    queryset = User.objects.get_queryset()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'study_program', 'interests']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']  # Default: newest first
