"""
Production configuration for Rady
"""


from rady.settings import *


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


ALLOWED_HOSTS = ("rady.benschubert.me",)

STATIC_ROOT = "/srv/rady/static/"

DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'CENSORED'


DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.postgresql_psycopg2",
        'NAME': "rady",
        "USER": "rady",
        "PASSWORD": "CENSORED",
        "HOST": "localhost"
    }
}

FCM_SETTINGS = {
    "FCM_SERVER_KEY": "CENSORED"
}


EMAIL_HOST = "ssl0.ovh.net"
EMAIL_PORT = "465"
EMAIL_HOST_USER = "rady@benschubert.me"
EMAIL_HOST_PASSWORD = "CENSORED"
EMAIL_USE_SSL = True
