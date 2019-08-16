from rest_framework import serializers
from .models import FoodCategory


class FoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = ("id", "user", "name", "created_at")
        read_only_fields = ("id", "user", "created_at")
