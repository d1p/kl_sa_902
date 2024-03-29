from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError

from .models import User


def save_user_information(user_instance: User, user_data: dict):
    user_instance.name = user_data.get("name", user_instance.name)
    user_instance.name_in_ar = user_data.get("name_in_ar", user_instance.name_in_ar)
    user_instance.email = user_data.get("email", user_instance.email)

    user_instance.locale = user_data.get("locale", user_instance.locale)
    user_instance.profile_picture = user_data.get(
        "profile_picture", user_instance.profile_picture
    )
    try:
        user_instance.save()
    except IntegrityError:
        raise ValidationError(
            {"user": {"email": [_("Email address is already registered")]}}
        )
    return user_instance


def register_basic_user(group_name: str, user_data: dict) -> User:
    group = Group.objects.get(name=group_name)

    if user_data.get("phone_number") is None:
        raise ValidationError(
            {"user": {"phone_number": ["This field may not be blank."]}}
        )
    if user_data.get("email") is None:
        raise ValidationError({"user": {"email": ["This field may not be blank."]}})

    if user_data.get("password") is None:
        raise ValidationError({"user": {"password": ["This field may not be blank."]}})

    try:
        user = User.objects.create(
            name=user_data.get("name"),
            name_in_ar=user_data.get("name_in_ar"),
            phone_number=user_data.get("phone_number"),
            email=user_data.get("email"),
            locale=user_data.get("locale", "en"),
        )

    except IntegrityError as e:
        if "email" in e.args[0]:
            field_name = "email_address"
            formal_field_name = "Email Address"
        else:
            field_name = "phone_number"
            formal_field_name = "Phone Number"

        raise ValidationError(
            {"user": {f"{field_name}": [f"{formal_field_name} is already registered"]}}
        )

    user.groups.add(group)
    user.set_password(user_data.get("password"))
    if user_data.get("profile_picture") is not None:
        user.profile_picture = user_data.get("profile_picture")
    user.save()

    return user
