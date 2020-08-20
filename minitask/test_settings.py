"""Settings overrides for tests"""

# pylint: disable=wildcard-import,unused-wildcard-import
from .settings import *


# This makes tests run waaaaay faster
# https://docs.djangoproject.com/en/3.1/topics/testing/overview/#speeding-up-the-tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
