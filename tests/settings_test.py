#!/usr/bin/env python

import unittest

from downspout import settings


class SettingsTest(unittest.TestCase):

    def test_required_settings(self):
        self.assertIsNotNone(settings.MEDIA_FOLDER)

    def test_bandcamp_settings(self):
        self.assertIsNotNone(settings.BANDCAMP_FRONT_URL)
        self.assertIsNotNone(settings.BANDCAMP_ALBUM_URL)

    def test_soundcloud_settings(self):
        self.assertIsNotNone(settings.SOUNDCLOUD_CLIENT_ID)
        self.assertIsNotNone(settings.SOUNDCLOUD_FRONT_URL)
        self.assertIsNotNone(settings.SOUNDCLOUD_RESOLVE_API)
        self.assertIsNotNone(settings.SOUNDCLOUD_TRACK_API)
        self.assertIsNotNone(settings.SOUNDCLOUD_MEDIA_URL)

    def test_vimeo_settings(self):
        self.assertIsNotNone(settings.VIMEO_USER_URL)

    def test_youtube_settings(self):
        self.assertIsNotNone(settings.YOUTUBE_USER_URL)
        self.assertIsNotNone(settings.YOUTUBE_VIDEO_URL)
