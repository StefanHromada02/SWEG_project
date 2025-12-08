from rest_framework import serializers
from .models import Comment
from domains.users.serializers import UserSerializer
from domains.posts.serializers import PostSerializer


class CommentSerializer(serializers.ModelSerializer):
    # User ID for output only
    user = serializers.IntegerField(read_only=True)
    # Nested serializers for read operations (optional, can be just IDs)
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Comment
        fields = ["id", "user", "user_details", "post", "text", "created_at"]
        read_only_fields = ["id", "user", "user_details", "created_at"]


class CommentCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating comments."""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Comment
        fields = ["post", "text", "user"]
