from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.account.models import User
from apps.account.serializers import PrivateUserSerializer
from apps.food.serializers import FoodAttributeMatrixSerializer, FoodAddOnSerializer
from apps.order.tasks import (
    send_order_invitation_accept_notification,
    send_new_order_in_cart_notification,
    send_order_item_invite_notification,
    send_order_item_invitation_accept_notification,
)
from apps.order.types import OrderStatusType, OrderInviteStatusType
from .models import (
    Order,
    OrderInvite,
    OrderItem,
    OrderItemInvite,
    OrderParticipant,
    OrderItemAddOn,
    OrderItemAttributeMatrix,
    Rating,
)


class BulkOrderInviteSerializer(serializers.Serializer):
    invited_users = serializers.ListField(child=serializers.IntegerField())
    order = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class OrderInviteSerializer(serializers.ModelSerializer):
    restaurant_id = serializers.IntegerField(
        source="order.restaurant.id", read_only=True
    )

    class Meta:
        model = OrderInvite
        fields = (
            "id",
            "invited_user",
            "order",
            "status",
            "restaurant_id",
            "invited_by",
            "created_at",
        )
        read_only_fields = ("id", "invited_by", "created_at")

    def update(self, instance: OrderInvite, validated_data):
        """
        Update should only be used by the invited user to accept or reject the request.
        """
        current_user = self.context["request"].user
        if instance.invited_user != current_user or instance.status != 0:
            raise PermissionDenied
        if validated_data.get("status") == 1:
            # Accepts
            order = instance.order
            order.order_participants.create(user=current_user)
            current_user.misc.last_order = order
            current_user.misc.last_order_in_checkout = False
            current_user.misc.last_restaurant = order.restaurant
            current_user.misc.last_order_type = order.order_type
            current_user.misc.save()
            instance.status = OrderInviteStatusType.ACCEPTED
            instance.save()
            send_order_invitation_accept_notification.delay(
                from_user=current_user.id, order_id=order.id
            )
        else:
            instance.status = OrderInviteStatusType.REJECTED
            instance.save()

        return instance


class BulkOrderItemInviteSerializer(serializers.Serializer):
    invited_users = serializers.ListField(child=serializers.IntegerField())
    order_item = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class OrderItemInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemInvite
        fields = (
            "id",
            "invited_user",
            "invited_by",
            "order_item",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "invited_by", "created_at")

    def update(self, instance: OrderItemInvite, validated_data):
        """
        Update should only be used by the invited user to accept or reject the request.
        """
        current_user = self.context["request"].user
        if instance.invited_user != current_user or instance.status != 0:
            raise PermissionDenied

        if validated_data.get("status") == 1:
            # Accepts
            order_item = instance.order_item
            order_item.shared_with.add(current_user)
            instance.status = 1
            instance.save()
            # Send necessary signals
            send_order_item_invitation_accept_notification.delay(
                from_user=current_user.id,
                order_id=order_item.order.id,
                item_id=order_item.id,
            )
        else:
            instance.status = 2
            instance.save()

        return instance


class OrderItemAddOnSerializer(serializers.ModelSerializer):
    food_add_on_details = FoodAddOnSerializer(source="food_add_on", read_only=True)

    class Meta:
        model = OrderItemAddOn
        fields = ("id", "food_add_on", "food_add_on_details", "created_at")
        read_only_fields = ("id", "food_add_on_details", "created_at")


class OrderItemAttributeMatrixSerializer(serializers.ModelSerializer):
    food_attribute_matrix_details = FoodAttributeMatrixSerializer(
        source="food_attribute_matrix", read_only=True
    )

    class Meta:
        model = OrderItemAttributeMatrix
        fields = (
            "id",
            "food_attribute_matrix",
            "food_attribute_matrix_details",
            "created_at",
        )
        read_only_fields = ("id", "food_attribute_matrix_details", "created_at")


class OrderItemSerializer(serializers.ModelSerializer):
    order_item_add_ons = OrderItemAddOnSerializer(many=True, required=False)
    order_item_attribute_matrices = OrderItemAttributeMatrixSerializer(
        many=True, required=False
    )
    invited_users = serializers.ListField(
        child=serializers.IntegerField(), required=False
    )
    food_item_price = serializers.DecimalField(
        source="food_item.price", read_only=True, decimal_places=3, max_digits=9
    )
    food_item_name = serializers.CharField(source="food_item.name", read_only=True)
    food_item_calorie = serializers.IntegerField(
        source="food_item.calorie", read_only=True
    )

    shared_with = serializers.SerializerMethodField()

    def get_shared_with(self, obj: OrderItem):
        return (
            obj.shared_with.all()
            .exclude(id=self.context["request"].user.id)
            .values_list("id", flat=True)
        )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "order",
            "food_item",
            "food_item_price",
            "food_item_name",
            "food_item_calorie",
            "quantity",
            "order_item_add_ons",
            "order_item_attribute_matrices",
            "invited_users",
            "status",
            "shared_with",
            "total_price",
            "shared_price",
            "added_by",
            "created_at",
        )
        read_only_fields = (
            "id",
            "added_by",
            "shared_with",
            "created_at",
            "total_price",
            "shared_price",
        )

    def create(self, validated_data):
        order = validated_data.get("order")

        if order.status == OrderStatusType.OPEN:
            order_item_addons = validated_data.pop("order_item_add_ons", [])
            order_item_attribute_matrices = validated_data.pop(
                "order_item_attribute_matrices", []
            )
            invited_users = validated_data.pop("invited_users", [])

            order_item = OrderItem.objects.create(**validated_data)

            for order_addon in order_item_addons:
                add_on = order_addon["food_add_on"]
                if (
                    OrderItemAddOn.objects.filter(
                        order_item=order_item, food_add_on=add_on
                    ).exists()
                    is False
                ):
                    OrderItemAddOn.objects.create(
                        order_item=order_item, food_add_on=add_on
                    )

            for order_attribute_matrix in order_item_attribute_matrices:
                attribute_matrix = order_attribute_matrix["food_attribute_matrix"]
                if (
                    OrderItemAttributeMatrix.objects.filter(
                        order_item=order_item, food_attribute_matrix=attribute_matrix
                    ).exists()
                    is False
                ):
                    OrderItemAttributeMatrix.objects.create(
                        order_item=order_item, food_attribute_matrix=attribute_matrix
                    )
            order_item.shared_with.add(validated_data.get("added_by"))
            order_item.refresh_from_db()

            send_new_order_in_cart_notification.delay(
                added_by=order_item.added_by.id,
                order_id=order.id,
                order_item_id=order_item.id,
            )

            for i_user in invited_users:
                try:
                    user = User.objects.get(id=i_user)
                    invite = order_item.order_item_invites.create(
                        invited_user=user, invited_by=validated_data.get("added_by")
                    )
                    send_order_item_invite_notification.delay(
                        from_user=order_item.added_by.id,
                        to_user=user.id,
                        invite_id=invite.id,
                        item_id=order_item.id,
                    )
                except User.DoesNotExist:
                    pass

            return order_item
        else:
            return ValidationError(
                {"non_field_errors": ["This order has been closed."]}
            )

    def update(self, instance: OrderItem, validated_data):
        current_user = self.context["request"].user

        if (
            instance.order.order_participants.filter(user=current_user).exists()
            is False
        ):
            raise PermissionDenied

        validated_data.pop("order")
        order_item_addons = validated_data.pop("order_item_add_ons", [])
        order_item_attribute_matrices = validated_data.pop(
            "order_item_attribute_matrices", []
        )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        OrderItemAddOn.objects.filter(order_item=instance).delete()
        OrderItemAttributeMatrix.objects.filter(order_item=instance).delete()

        for order_addon in order_item_addons:
            add_on = order_addon["food_add_on"]
            if (
                OrderItemAddOn.objects.filter(
                    order_item=instance, food_add_on=add_on
                ).exists()
                is False
            ):
                OrderItemAddOn.objects.create(order_item=instance, food_add_on=add_on)

        for order_attribute_matrix in order_item_attribute_matrices:
            attribute_matrix = order_attribute_matrix["food_attribute_matrix"]
            if (
                OrderItemAttributeMatrix.objects.filter(
                    order_item=instance, food_attribute_matrix=attribute_matrix
                ).exists()
                is False
            ):
                OrderItemAttributeMatrix.objects.create(
                    order_item=instance, food_attribute_matrix=attribute_matrix
                )
        instance.refresh_from_db()
        return instance


class OrderParticipantSerializer(serializers.ModelSerializer):
    user = PrivateUserSerializer()

    class Meta:
        model = OrderParticipant
        fields = ("user", "created_at", "order")


class OrderSerializer(serializers.ModelSerializer):
    order_participants = OrderParticipantSerializer(
        required=False, read_only=True, many=True
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "order_type",
            "restaurant",
            "table",
            "order_item_set",
            "order_participants",
            "confirmed",
            "status",
            "created_by",
            "created_at",
        )
        read_only_fields = (
            "id",
            "status",
            "created_by",
            "created_at",
            "order_item_set",
            "confirmed",
        )

    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
        order.order_participants.create(user=order.created_by)
        order.created_by.misc.last_order = order
        order.created_by.misc.last_order_in_checkout = False
        order.created_by.misc.last_restaurant = order.restaurant
        order.created_by.misc.last_order_type = order.order_type
        order.created_by.misc.save()
        return order


class ConfirmSerializer(serializers.Serializer):
    sure = serializers.BooleanField(required=True)


class OrderRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = (
            "id",
            "order",
            "restaurant",
            "user",
            "food_item_rating",
            "restaurant_rating",
            "customer_service_rating",
            "application_rating",
            "created_at",
        )
        read_only_field = ("id", "restaurant", "user", "created_at")

    def create(self, validated_data):
        order: Order = validated_data.get("order")
        user: User = validated_data.get("user")
        if order.status not in [OrderStatusType.CHECKOUT, OrderStatusType.COMPLETED]:
            raise ValidationError(
                {"non_field_error": ["Order has not been checked out or completed."]}
            )
        if order.order_participants.filter(user=user).exists() is False:
            raise PermissionDenied

        instance = Rating.objects.create(**validated_data)

        user.misc.last_order = None
        user.misc.last_order_in_checkout = None
        user.misc.last_order_type = None
        user.misc.last_restaurant = None

        return instance


class OrderIsReadySerializer(serializers.Serializer):
    time = serializers.IntegerField(required=True)
