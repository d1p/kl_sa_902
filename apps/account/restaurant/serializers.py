from django.db import transaction
from rest_framework import serializers

from apps.account.restaurant.models import Restaurant, Category, RestaurantTable
from apps.account.restaurant.tasks import generate_table_qr_code
from apps.account.serializers import UserSerializer
from apps.account.utils import save_user_information, register_basic_user


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "name_in_ar")


class RestaurantSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Restaurant
        fields = ("user",)

    def create(self, validated_data):
        user = register_basic_user("Restaurant", validated_data.pop("user", {}))
        user.is_active = True
        user.save()
        restaurant = Restaurant.objects.create(user=user)
        return restaurant

    def update(self, instance, validated_data):
        with transaction.atomic():
            save_user_information(instance.user, validated_data.pop("user", {}))
            if validated_data.get("cover_picture") is not None:
                instance.cover_picture = validated_data.get(
                    "cover_picture", instance.cover_picture
                )
            instance.restaurant_type = validated_data.get(
                "restaurant_type", instance.restaurant_type
            )
            instance.full_address = validated_data.get(
                "full_address", instance.full_address
            )
            instance.online = validated_data.get("online", instance.online)

            return instance


class RestaurantTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantTable
        fields = ("id", "name", "qr_code")
        read_only_fields = ("id", "qr_code")

    def create(self, validated_data):
        instance = RestaurantTable.objects.create(**validated_data)
        generate_table_qr_code.delay(instance.id)
        instance.refresh_from_db()
        return instance

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name")
        instance.save()
        return instance
