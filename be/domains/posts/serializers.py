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