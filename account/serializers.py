# account/serializers.py
from rest_framework import serializers
from .models import User, Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Profile model
    - qr_code is read-only (auto-generated)
    """
    class Meta:
        model = Profile
        fields = [
            "id",
            "image_profile",
            "qr_code",
            "uuid",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["qr_code", "uuid", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for custom User model
    - phone_number is the USERNAME_FIELD (login field)
    """
    profile = ProfileSerializer(read_only=True)  # Nested profile

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "role",
            "profile",
        ]
        read_only_fields = ["id", "role"]  # You can make role editable if you want


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user data
    """
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

