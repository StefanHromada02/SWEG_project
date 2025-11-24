from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "study_program", "interests", "created_at"]
        read_only_fields = ["created_at"]
    
    def validate_interests(self, value):
        """Validate that interests list has max 5 items."""
        if len(value) > 5:
            raise serializers.ValidationError("Maximum 5 interests allowed")
        return value
