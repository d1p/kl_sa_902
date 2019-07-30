from conf.settings import *

DATABASES = {"default": env.db("TEST_DATABASE_URL")}
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
REQUIRED_PROFILE_COMPLETION = 30
