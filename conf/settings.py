import os
from datetime import timedelta

import environ
from django.utils.translation import ugettext_lazy as _

env = environ.Env()
root_path = environ.Path(__file__) - 2

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = []


# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "storages",
    "rest_framework_swagger",
    "fcm_django",
    "drf_yasg",
]

CORE_APPS = ["apps.account", "apps.account.customer"]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CORE_APPS

AUTH_USER_MODEL = "account.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "conf.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ["templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "conf.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {"default": env.db()}

CACHES = {"default": env.cache()}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGES = [("en", _("English")), ("ar", _("Arabic"))]
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = False
USE_TZ = True
USER_DEFAULT_LANGUAGE = "en"
ADMIN_TIMEZONE = "Asia/Riyadh"
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 5,
    "DATETIME_FORMAT": "%Y-%m-%d %H:%m:%S",
    "DATETIME_INPUT_FORMATS": ["iso-8601", "%Y-%m-%d %H:%m:%S"],
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID", default="")
AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_ENDPOINT_URL = env.str("AWS_S3_ENDPOINT_URL", default="")
AWS_LOCATION = env.str("AWS_LOCATION", default="")
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_DEFAULT_ACL = "public-read"

if DEBUG is False:
    STATIC_URL = "https://%s/%s/" % (AWS_S3_ENDPOINT_URL, AWS_LOCATION)
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
else:
    STATIC_URL = "/static/"

# Firebase
FCM_DJANGO_SETTINGS = {
    "FCM_SERVER_KEY": env.str("FCM_SERVER_KEY", default=""),
    "ONE_DEVICE_PER_USER": False,
    "DELETE_INACTIVE_DEVICES": False,
}

# JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("JWT",),
}

# SMS
TWILIO_ACCOUNT_SID = env.str("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = env.str("TWILIO_AUTH_TOKEN")

# Email
ANYMAIL = {"MAILGUN_API_KEY": env.str("MAILGUN_API_KEY")}
DEFAULT_SERVER_EMAIL = env.str("DEFAULT_SERVER_EMAIL")
DEFAULT_ACCOUNT_EMAIL = env.str("DEFAULT_ACCOUNT_EMAIL")
DEFAULT_NOTIFICATION_EMAIL = env.str("DEFAULT_NOTIFICATION_EMAIL")
EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"

# Celery
CELERY_BROKER_URL = env.str("REDIS_URL")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
BROKER_POOL_LIMIT = 1
BROKER_TRANSPORT_OPTIONS = {"max_connections": 2}

if DEBUG is False:
    RAVEN_CONFIG = {"dsn": env.str("RAVEN_DSN", default="")}

LOGIN_URL = "/admin/"

# Logging
LOGS_ROOT = env("LOGS_ROOT", default=root_path("logs"))
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console_format": {"format": "%(name)-12s %(levelname)-8s %(message)s"},
        "file_format": {
            "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s"
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console_format",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOGS_ROOT, "django.log"),
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "file_format",
        },
    },
    "loggers": {
        "django": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "apps": {"level": "DEBUG", "handlers": ["console", "file"], "propagate": False},
    },
}
