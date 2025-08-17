from rest_framework import serializers
from .models import Manager

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['id', 'user', 'bank_account_number', 'created_at']
        read_only_fields = ['id', 'created_at']