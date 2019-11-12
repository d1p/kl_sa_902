from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from apps.account.serializers import PublicUserSerializer
from .models import (
    FoodCategory,
    FoodItem,
    FoodAddOn,
    FoodAttribute,
    FoodAttributeMatrix,
)


class FoodAddOnSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodAddOn
        fields = ("id", "food", "name", "price")
        read_only_fields = ("id",)

    def create(self, validated_data):
        user = self.context["request"].user
        food = validated_data.get("food")
        if food.user != user:
            raise PermissionDenied
        return FoodAddOn.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        food = validated_data.get("food")
        if food.user != user:
            raise PermissionDenied

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class FoodAttributeMatrixSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source="attribute.name", read_only=True)

    class Meta:
        model = FoodAttributeMatrix
        fields = ("id", "name", "attribute", "attribute_name")
        read_only_fields = ("id",)

    def create(self, validated_data):
        user = self.context["request"].user
        attribute = validated_data.get("attribute")
        if attribute.food.user != user:
            raise PermissionDenied
        return FoodAttributeMatrix.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        attribute = validated_data.get("attribute")
        if attribute.food.user != user:
            raise PermissionDenied
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class FoodAttributeSerializer(serializers.ModelSerializer):
    attribute_matrix = FoodAttributeMatrixSerializer(many=True, read_only=True)

    class Meta:
        model = FoodAttribute
        fields = ("id", "name", "food", "attribute_matrix")
        read_only_fields = ("id",)

    def create(self, validated_data):
        user = self.context["request"].user
        food = validated_data.get("food")
        if food.user != user:
            raise PermissionDenied
        return FoodAttribute.objects.create(**validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        food = validated_data.get("food")
        if food.user != user:
            raise PermissionDenied
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class FoodCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = ("id", "user", "name", "created_at")
        read_only_fields = ("id", "user", "created_at")


class FoodItemSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    addons = FoodAddOnSerializer(many=True, read_only=True)
    attributes = FoodAttributeSerializer(many=True, read_only=True)

    addons_display = FoodAddOnSerializer(many=True, read_only=True)
    attributes_display = FoodAttributeSerializer(many=True, read_only=True)

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
            "addons",
            "attributes",
            "addons_display",
            "attributes_display",
        )

        read_only_fields = ("id", "user")
        extra_kwargs = {"category": {"required": True}}
