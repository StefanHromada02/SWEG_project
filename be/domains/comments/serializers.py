from rest_framework import serializers
from .models import Comment
from domains.users.serializers import UserSerializer
from domains.posts.serializers import PostSerializer


class CommentSerializer(serializers.ModelSerializer):
    # Nested serializers for read operations (optional, can be just IDs)
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Comment
        fields = ["id", "user", "user_details", "post", "text", "created_at"]
        read_only_fields = ["created_at"]


class CommentCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating comments."""
    class Meta:
        model = Comment
        fields = ["id", "user", "post", "text", "created_at"]
        read_only_fields = ["created_at"]
