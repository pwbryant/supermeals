"""
Django settings for supermeals project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import json
import os

# from dotenv import load_dotenv
from pathlib import Path

import json
import os

from django.core.exceptions import ImproperlyConfigured

secrets_file = Path(Path(__file__).parent, "secrets.json")
with open(secrets_file) as f:
    secrets = json.load(f)


def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent.parent


# DEPLOY SETTINGS
DEBUG = get_secret("DEBUG")
SECRET_KEY = get_secret("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
# ALLOWED_HOSTS = ['mlab.us-east-2.elasticbeanstalk.com', '127.0.0.1']
ALLOWED_HOSTS = get_secret("ALLOWED_HOSTS")

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "meals",
    "django_extensions",
    "widget_tweaks",
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

ROOT_URLCONF = "supermeals.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": (Path(BASE_DIR, "templates/"),),
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "supermeals.wsgi.application"

# Database

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
        'ENGINE': get_secret('DB_ENGINE'),
        'NAME': get_secret('DB_NAME'),
        'USER': get_secret('DB_USER'),
        'PASSWORD': get_secret('DB_PASSWORD'),
        'HOST': get_secret('DB_HOST'),
        'PORT': get_secret('DB_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
        ),
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

# USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = Path(BASE_DIR, "static")
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, 'static'),
# )

# Redirect to home URL after login (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = "/"

NOTEBOOK_ARGUMENTS = [
    '--ip', '0.0.0.0',
    '--port', '8888',
    '--no-browser'
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'timestamp': {
        'format': '%(asctime)s %(message)s',
        'datefmt': '%Y-%m-%d %H:%M'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'werkzeug': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
