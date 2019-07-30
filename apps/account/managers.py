from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def _create_user(
        self,
        phone_number: str,
        email: str,
        password: str,
        is_staff: bool,
        is_superuser: bool,
        **extra_fields,
    ):
        if not phone_number:
            raise ValueError("The given phone number must be set.")

        if email:
            email = self.normalize_email(email)

        phone_number = phone_number

        user = self.model(
            phone_number=phone_number,
            email=email,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, phone_number: str, password=None, **extra_fields):
        return self._create_user(
            phone_number, None, password, False, False, **extra_fields
        )

    def create_superuser(
        self, phone_number: str, email: str, password: str, **extra_fields
    ):
        return self._create_user(
            phone_number, email, password, True, True, **extra_fields
        )
