from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    interests = serializers.ListField(
        child=serializers.CharField(max_length=100),
        max_length=5,
        required=False,
        allow_empty=True,
        default=list
    )
    
    class Meta:
        model = User
        fields = ["id", "name", "email", "study_program", "interests", "created_at"]
        read_only_fields = ["created_at"]
    
    def validate_email(self, value):
        """Validate that email ends with @technikum-wien.at"""
        if not value.endswith("@technikum-wien.at"):
            raise serializers.ValidationError(
                "Only email addresses ending with @technikum-wien.at are allowed"
            )
        return value
    
    def validate_interests(self, value):
        """Validate that interests list has max 5 items."""
        if value and len(value) > 5:
            raise serializers.ValidationError("Maximum 5 interests allowed")
        return value if value else []
