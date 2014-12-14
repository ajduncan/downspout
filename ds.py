#!/usr/bin/env python

import os

from downspout.settings import *
from downspout.bandcamp import *
from downspout.soundcloud import *
from downspout.youtube import *
from downspout.vimeo import *


def fetch_all(filename):
    records = open(filename, 'r')
    for media in records:
        [app, artist] = [item.strip() for item in media.split(',')]
        if app.lower() == 'soundcloud':
            soundcloud_fetch_media(
                '{0}/{1}'.format(SOUNDCLOUD_FRONT_URL, artist))
        if app.lower() == 'bandcamp':
            bandcamp_fetch_media(artist)
        if app.lower() == 'youtube':
            youtube_fetch_media(artist)
        if app.lower() == 'vimeo':
            vimeo_fetch_media(artist)


if __name__ == "__main__":
    fetch_all('media.txt')
