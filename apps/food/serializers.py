from rest_framework import serializers

from apps.account.serializers import PublicUserSerializer
from .models import FoodCategory, FoodItem


class FoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = ("id", "user", "name", "created_at")
        read_only_fields = ("id", "user", "created_at")


class FoodItemSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = FoodItem
        fields = (
            "id",
            "category",
            "category_name",
            "name",
            "user",
            "picture",
            "price",
            "calorie",
            "is_active",
        )

        read_only_fields = ("id", "user")
