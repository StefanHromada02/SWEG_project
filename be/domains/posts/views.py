# posts/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Post
from .serializers import PostSerializer, PostCreateSerializer
from services.minio_storage import minio_storage


@extend_schema_view(
    list=extend_schema(tags=['Posts']),
    create=extend_schema(tags=['Posts']),
    retrieve=extend_schema(tags=['Posts']),
    update=extend_schema(tags=['Posts']),
    partial_update=extend_schema(tags=['Posts']),
    destroy=extend_schema(tags=['Posts'])
)
class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing posts.
    
    Provides CRUD operations and search functionality for posts.
    """
    queryset = Post.objects.get_queryset()
    serializer_class = PostSerializer
    
    def get_serializer_class(self):
        """Use PostCreateSerializer for create/update operations."""
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateSerializer
        return PostSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'text']  # Suche in Titel und Text
    ordering_fields = ['created_at', 'title']  # Sortierung möglich
    ordering = ['-created_at']  # Standard: Neueste zuerst
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """
        Upload image to MinIO before saving post.
        User is automatically set by serializer's HiddenField(CurrentUserDefault()).
        """
        image_file = self.request.FILES.get('image_file')
        image_path = None
        
        if image_file:
            # Upload to MinIO
            image_path = minio_storage.upload_image(image_file)
            if not image_path:
                return Response(
                    {"error": "Failed to upload image"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Save with MinIO path (user is set automatically by serializer)
        serializer.save(image=image_path or "")
    
    def perform_update(self, serializer):
        """
        Handle image update: delete old, upload new.
        """
        instance = serializer.instance
        old_image = instance.image
        
        image_file = self.request.FILES.get('image_file')
        
        if image_file:
            # Delete old image if exists
            if old_image:
                minio_storage.delete_image(old_image)
            
            # Upload new image
            image_path = minio_storage.upload_image(image_file)
            if not image_path:
                return Response(
                    {"error": "Failed to upload image"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            serializer.save(image=image_path)
        else:
            serializer.save()
    
    def perform_destroy(self, instance):
        """
        Delete image from MinIO when post is deleted.
        """
        if instance.image:
            minio_storage.delete_image(instance.image)
        instance.delete()

    @extend_schema(
        tags=['Posts'],
        summary="Get user's posts",
        description="Returns all posts for the current authenticated user",
        responses={200: PostSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        # Filter posts by the authenticated user
        posts = Post.objects.filter(user=request.user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

