"""Defines various helpers for testing the rady application."""

import shutil
import tempfile
from django.conf import settings
from django.conf.urls.static import static
from django.test.runner import DiscoverRunner


__author__ = "Benjamin Schubert <ben.c.schubert@gmail.com>"


urls = __import__(settings.ROOT_URLCONF).urls.urlpatterns


class MediaAwareTestRunnerMixin:
    """
    This is a mixin to enable media handling when testing with Django.

    This will ensure the media root is setup before launching the tests and
    will add the needed urls to the list of url patterns.
    """
    _original_media_root = None
    _temporary_media_root = None
    _media_url = None

    def setup_test_environment(self):
        """Setup the test environment, by adding the MEDIA_ROOT and MEDIA_URL correctly."""
        # noinspection PyUnresolvedReferences
        super().setup_test_environment()
        self._original_media_root = settings.MEDIA_ROOT
        self._temporary_media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temporary_media_root

        old_debug_setting = settings.DEBUG
        settings.DEBUG = True
        self._media_url = static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        settings.DEBUG = old_debug_setting

        urls.extend(self._media_url)

    def teardown_test_environment(self):
        """
        Cleanup the environment at the end.

        This restores the original state of the aplication and deletes the MEDIA_ROOT.
        """
        # noinspection PyUnresolvedReferences
        super().teardown_test_environment()
        shutil.rmtree(self._temporary_media_root, ignore_errors=True)
        settings.MEDIA_ROOT = self._original_media_root

        for url in self._media_url:
            urls.remove(url)


class RadyTestRunner(MediaAwareTestRunnerMixin, DiscoverRunner):
    """The default test runner for the Rady project."""
