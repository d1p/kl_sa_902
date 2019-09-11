from fcm_django.models import FCMDevice

from apps.account.models import User


def send_push_notification(user: User, title: str, body: str, data={}):
    """
    This function sends push notification based on the device type
    :param user:
    :param title:
    :param body:
    :param data:
    :return:
    """

    ios_devices = FCMDevice.objects.filter(user=user, active=True, type="ios")
    ios_devices.send_message(title, body, data=data)
    web_devices = FCMDevice.objects.filter(user=user, active=True, type="web")
    web_devices.send_message(title, body, data=data)
    android_devices = FCMDevice.objects.filter(user=user, active=True, type="android")

    notification_data = {"title": title, "body": body}
    data["notification_data"] = notification_data
    android_devices.send_data_message(data_message=data)
