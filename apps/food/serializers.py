from rest_framework import serializers

from apps.account.serializers import PublicUserSerializer
from .models import FoodCategory, FoodItem, FoodAttributeMatrix, FoodAttribute, FoodAddOn


class FoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = ("id", "user", "name", "created_at")
        read_only_fields = ("id", "user", "created_at")


class FoodItemSerializer(serializers.ModelSerializer):
    category = FoodCategorySerializer()
    user = PublicUserSerializer(read_only=True)

    class Meta:
        model = FoodItem
        fields = ("id", "category", "name", "user", "picture", "price",
                  "calorie", "is_active", )
