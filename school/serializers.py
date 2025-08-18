from rest_framework import serializers
from .models import School
from manager.models import Manager
from manager.serializers import ManagerSerializer


class SchoolSerializer(serializers.ModelSerializer):
    manager = ManagerSerializer(read_only=True)
    manager_id = serializers.PrimaryKeyRelatedField(
        queryset=Manager.objects.all(),
        source="manager",
        write_only=True
    )

    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "address",
            "email",
            "is_active",
            "created_at",
            "manager",
            "manager_id",
        ]
        read_only_fields = ["id", "created_at", "manager"]
