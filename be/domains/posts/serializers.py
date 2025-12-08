from rest_framework import serializers
from .models import Post
from domains.users.serializers import UserSerializer


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts - excludes user field."""
    image_file = serializers.ImageField(write_only=True, required=False)
    # User will be set programmatically from request context, not from input data
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Post
        fields = ["title", "text", "image_file", "user"]
        
    def validate_image_file(self, value):
        """Validiere Bildgröße und Format."""
        # Max 5MB
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image size must be less than 5MB")
        
        # Erlaubte Formate
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"Only JPEG, PNG, GIF, and WebP images are allowed"
            )
        
        return value
    
    def create(self, validated_data):
        """
        Create post - user is already set by HiddenField(CurrentUserDefault()).
        """
        # Remove image_file from validated data
        validated_data.pop('image_file', None)
        # User is already in validated_data from HiddenField
        return super().create(validated_data)


class PostSerializer(serializers.ModelSerializer):
    # Akzeptiert Upload von Bild-Dateien
    image_file = serializers.ImageField(write_only=True, required=False)
    # URL-Pfad wird automatisch gesetzt (read-only)
    image = serializers.CharField(read_only=True)
    # User ID for output only
    user = serializers.IntegerField(read_only=True)
    # Nested user details for read operations
    user_details = UserSerializer(source='user', read_only=True)
    # Comment count
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ["id", "user", "user_details", "title", "text", "image", "image_file", "created_at", "comment_count"]
        read_only_fields = ["id", "user", "user_details", "image", "created_at", "comment_count"]  # User is set automatically from authentication
        
    def get_comment_count(self, obj):
        """Return the number of comments for this post."""
        return obj.comments.count()
        
    def validate_image_file(self, value):
        """Validiere Bildgröße und Format."""
        # Max 5MB
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image size must be less than 5MB")
        
        # Erlaubte Formate
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                f"Only JPEG, PNG, GIF, and WebP images are allowed"
            )
        
        return value
    
    def create(self, validated_data):
        """
        Remove image_file from validated_data before creating Post.
        User should be set in view's perform_create, not here.
        """
        validated_data.pop('image_file', None)
        # User must be provided by the view
        if 'user' not in validated_data:
            raise serializers.ValidationError({"user": "Authentication required to create posts"})
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Remove image_file from validated_data before updating Post."""
        validated_data.pop('image_file', None)
        return super().update(instance, validated_data)