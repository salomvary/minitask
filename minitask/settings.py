"""
Django settings for minitask project.

Generated by 'django-admin startproject' using Django 3.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import distutils.util
import os
from pathlib import Path

import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "k@4+jg3h24i=#e6objmu6j4bf7@r62zckm=l23kg(2i!(@5%(+"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = bool(distutils.util.strtobool(os.environ.get("DEBUG", "True")))

# Enable Heroku specific logging
# https://github.com/heroku/django-heroku/blob/master/django_heroku/core.py#L117
if bool(distutils.util.strtobool(os.environ.get("ENABLE_HEROKU_LOGGING", "False"))):
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": (
                    "%(asctime)s [%(process)d] [%(levelname)s] "
                    + "pathname=%(pathname)s lineno=%(lineno)s "
                    + "funcname=%(funcName)s %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "simple": {"format": "%(levelname)s %(message)s"},
        },
        "handlers": {
            "null": {"level": "DEBUG", "class": "logging.NullHandler",},
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "loggers": {"testlogger": {"handlers": ["console"], "level": "INFO",}},
    }
elif bool(distutils.util.strtobool(os.environ.get("DEBUG_SQL", "False"))):
    LOGGING = {
        "version": 1,
        "handlers": {
            # "console": {"class": "logging.StreamHandler",},
            "sqlhandler": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "sqlformatter",
            },
        },
        "formatters": {
            "sqlformatter": {
                "()": "ddquery.SqlFormatter",
                "format": "%(levelname)s %(message)s",
            },
        },
        "loggers": {
            "django.db.backends": {"handlers": ["sqlhandler"], "level": "DEBUG",},
        },
        # "root": {"handlers": ["console"],},
    }

ALLOWED_HOSTS = [os.environ["ALLOWED_HOSTS"]] if "ALLOWED_HOSTS" in os.environ else []


# Application definition

INSTALLED_APPS = [
    "tasks.apps.TasksConfig",
    "auth.apps.AuthConfig",
    "taggit",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "minitask.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "minitask.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if "DATABASE_URL" in os.environ:
    # Configure Django from DATABASE_URL environment variable
    DATABASES = {"default": dj_database_url.config(ssl_require=True)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "en-us")

TIME_ZONE = os.environ.get("TIME_ZONE", "UTC")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"

# Django does not serve static files in production. As long as
# we don't use a CDN, use WhiteNoiseMiddleware in production
if os.environ.get("SERVE_STATIC", False):
    # Set up static assets on Heroku
    # https://devcenter.heroku.com/articles/django-assets
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.9/howto/static-files/
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

    # Extra places for collectstatic to find static files.
    STATICFILES_DIRS = (
        # os.path.join(BASE_DIR, 'static'),
    )

    # Insert Whitenoise Middleware.
    MIDDLEWARE = tuple(
        ["whitenoise.middleware.WhiteNoiseMiddleware"] + list(MIDDLEWARE)
    )

    # Enable GZip.
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

LOGIN_URL = "/accounts/login/"
