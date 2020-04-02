import requests
from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from random import randrange

from utils.file import RandomFileName
from .managers import CustomUserManager
from .types import ProfileType

_PHONE_REGEX = RegexValidator(
    regex=r"\d{10}",
    message=_(
        "Phone number must be 10 digits."
    ),
)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(
        max_length=50, db_index=True, help_text=_("Users name / Restaurants name")
    )
    name_in_ar = models.CharField(
        max_length=50, null=True, blank=True, help_text=_("Name in arabic")
    )
    phone_number = models.CharField(
        validators=[_PHONE_REGEX], max_length=17, unique=True
    )
    phone_number_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Checks if the user has a verified phone number."),
    )

    email = models.EmailField(
        _("Email Address"), blank=True, null=True, db_index=True, unique=True
    )

    profile_picture = models.ImageField(
        _("Profile Picture"),
        upload_to=RandomFileName("user/profile-picture/"),
        default="user/profile-picture/default.png",
        null=True,
        blank=True,
    )

    is_staff = models.BooleanField(
        _("Staff status"),
        default=False,
        help_text=_("Designates whether this user can log into the admin site."),
    )
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active."
            "Unselect this instead of deleting the account"
        ),
    )

    locale = models.CharField(
        max_length=2, choices=settings.LANGUAGES, default=settings.USER_DEFAULT_LANGUAGE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    objects = CustomUserManager()
    USERNAME_FIELD = "phone_number"

    REQUIRED_FIELDS = ["email"]

    def __str__(self) -> str:
        return self.name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user if the user emial exists."""
        if self.email:
            send_mail(subject, message, from_email, [self.email], **kwargs)
        else:
            raise ValueError("User does not an email address.")

    def sms_user(self, body: str):
        """ Send a sms to the user """
        if settings.UNIT_TESTING:
            pass
        x = f"http://www.jawalbsms.ws/api.php/sendsms?user=kol&pass=20190710sSKol&to={self.phone_number}&message={body}&sender=kol"
        r = requests.get(x)

        print(f"Request: {x}\nResponse: {r.content}")

    @property
    def profile(self) -> object:
        """
        Returns child profile if available, else None
        """
        if self.profile_type == ProfileType.CUSTOMER:
            return self.customer
        elif self.profile_type is ProfileType.RESTAURANT:
            return self.restaurant
        else:
            return None

    @property
    def profile_type(self) -> str:
        """ Returns users profile type by filtering groups """
        if self.is_superuser or self.is_staff:
            return ProfileType.SUPERUSER

        if self.groups.filter(name="Customer").exists():
            return ProfileType.CUSTOMER
        elif self.groups.filter(name="Restaurant").exists():
            return ProfileType.RESTAURANT
        else:
            return "None"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class Token(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Phone number verification for {self.user}"

    @staticmethod
    def has_sent_recently(user: User) -> bool:
        """
        checks if the user has requested for a phone number verification in last 1 minutes.
        """
        created_time = timezone.datetime.now() - timezone.timedelta(minutes=1)
        return Token.objects.filter(user=user, created_at__gte=created_time).exists()

    class Meta:
        get_latest_by = "created_at"

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.code = randrange(100_0, 999_9)
        super(Token, self).save(*args, **kwargs)


class ForgotPasswordToken(Token):
    def __str__(self):
        return f"{self.user} : {self.code}"


class VerifyPhoneToken(Token):
    def __str__(self):
        return f"{self.user}: {self.code}"


class ChangePhoneNumberToken(Token):
    new_phone_number = models.CharField(
        validators=[_PHONE_REGEX], max_length=17, db_index=True
    )
    old_phone_number = models.CharField(
        validators=[_PHONE_REGEX], max_length=17, db_index=True
    )

    def __str__(self):
        return (
            f"{self.user}: Old: {self.old_phone_number}, New: {self.new_phone_number}"
        )
