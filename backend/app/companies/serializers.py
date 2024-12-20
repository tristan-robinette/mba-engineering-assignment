from rest_framework import serializers

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ["id", "name", "description", "total_bookings"]
        read_only_fields = ["total_bookings"]
