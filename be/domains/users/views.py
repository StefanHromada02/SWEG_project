from rest_framework import viewsets, filters
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import User
from .serializers import UserSerializer


@extend_schema_view(
    list=extend_schema(tags=['Users']),
    create=extend_schema(tags=['Users']),
    retrieve=extend_schema(tags=['Users']),
    update=extend_schema(tags=['Users']),
    partial_update=extend_schema(tags=['Users']),
    destroy=extend_schema(tags=['Users'])
)
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
