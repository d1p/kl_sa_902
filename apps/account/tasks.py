from apps.account.models import ForgotPasswordToken
from conf.celery import app
from .models import User


@app.task
def send_forgot_password_sms(instance: ForgotPasswordToken):
    pass


@app.task
def send_password_change_alert(user_id: int):
    user = User.objects.get(id=user_id)
    user.sms_user(
        f"Your Kole password has been changed. "
        f"If you haven't made this change then please reset your password."
    )
