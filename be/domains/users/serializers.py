from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email", "study_program", "interests", "created_at"]
        read_only_fields = ["created_at"]
    
    def validate_email(self, value):
        """Validate that email ends with @technikum-wien.at."""
        if not value.endswith("@technikum-wien.at"):
            raise serializers.ValidationError(
                "Email must end with @technikum-wien.at"
            )
        return value.lower()
    
    def validate_interests(self, value):
        """Validate that interests list has max 5 items."""
        if len(value) > 5:
            raise serializers.ValidationError("Maximum 5 interests allowed")
        return value
