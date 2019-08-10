from django.db import transaction
from rest_framework import serializers

from apps.account.restaurant.models import Restaurant
from apps.account.serializers import UserSerializer
from apps.account.utils import save_user_information, register_basic_user


class RestaurantSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Restaurant
        fields = ("user",)

    def create(self, validated_data):
        user = register_basic_user("Restaurant", validated_data.pop("user", {}))

        restaurant = Restaurant.objects.create(user=user)
        return restaurant

    def update(self, instance, validated_data):
        with transaction.atomic():
            save_user_information(instance.user, validated_data.pop("user", {}))
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
