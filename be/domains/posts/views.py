# posts/views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Post
from .serializers import PostSerializer
from services.minio_storage import minio_storage

class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing posts.
    
    Provides CRUD operations and search functionality for posts.
    """
    queryset = Post.objects.get_queryset()
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'text']  # Suche in Titel und Text
    ordering_fields = ['created_at', 'title']  # Sortierung möglich
    ordering = ['-created_at']  # Standard: Neueste zuerst

    def perform_create(self, serializer):
        """
        Upload image to MinIO before saving post.
        """
        image_file = self.request.FILES.get('image_file')
        image_path = None
        
        if image_file:
            # Upload to MinIO
            image_path = minio_storage.upload_image(image_file)
            if not image_path:
                # Raise validation error instead of returning Response
                raise ValidationError({"image_file": "Failed to upload image"})
        
        # Save with MinIO path
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
                raise ValidationError({"image_file": "Failed to upload image"})
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
        summary="Get user's posts",
        description="Returns all posts for the current user",
        responses={200: PostSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        posts = Post.objects.get_queryset()
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

