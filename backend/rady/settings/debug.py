"""Defines the debug configuration for Rady."""


from rady.settings import *  # noqa


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c$9+%3*wlc^zt$^(zys5jr!m%h1r!vk=t9i3oo!cv5*fq)84wm'  # noqa

DEBUG = True


DATABASES = {
    'default': {
        'ENGINE': "django.db.backends.sqlite3",
        'NAME': "rady.db",
    }
}
