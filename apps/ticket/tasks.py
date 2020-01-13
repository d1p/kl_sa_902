from conf.celery import app
from utils.fcm import send_push_notification
from .models import RestaurantMessage


@app.task
def send_new_ticket_notification():
    pass


@app.task
def send_message_notification(message_id: int):
    message = RestaurantMessage.objects.get(id=message_id)
    # This is a real user, send a push notification to the users device.
    data = {
        "notification_id": 0,
        "notification_action": "NEW_MESSAGE",
        "id": message.id,
        "sender": message.sender.id,
        "receiver": message.ticket.created_by.id,
        "sender_name": message.sender.name,
        "sender_profile_picture": message.sender.profile_picture.url,
        "text": message.text,
    }
    print(data)
    send_push_notification(
        user=message.ticket.created_by,
        title=message.sender.name,
        body=message.text,
        data=data,
    )
    print("OK!")
