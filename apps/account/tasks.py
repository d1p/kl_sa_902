from conf.celery import app
from apps.account.models import ForgotPasswordToken
from django.utils.translation import ugettext_lazy as _


@app.task
def send_forgot_password_sms(instance: ForgotPasswordToken):
    message = _("")
    instance.user.sms_user()
