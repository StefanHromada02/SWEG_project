from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    # Akzeptiert Upload von Bild-Dateien
    image_file = serializers.ImageField(write_only=True, required=False)
    # URL-Pfad wird automatisch gesetzt (read-only)
    image = serializers.CharField(read_only=True)
    
    class Meta:
        model = Post
        fields = ["id", "user", "title", "text", "image", "image_file", "created_at"]
        
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
        Custom create to remove image_file from validated_data.
        Image upload is handled in the view's perform_create.
        """
        # Remove image_file if present (it's write-only and not a model field)
        validated_data.pop('image_file', None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Custom update to remove image_file from validated_data.
        Image upload is handled in the view's perform_update.
        """
        # Remove image_file if present (it's write-only and not a model field)
        validated_data.pop('image_file', None)
        return super().update(instance, validated_data)