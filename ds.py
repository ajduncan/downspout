#!/usr/bin/env python

import os

from downspout import bandcamp, settings, soundcloud, youtube, vimeo

# Set the location to your media folder if desired.  The default will save to ./media.
# settings.MEDIA_FOLDER = './downloads'


def fetch_all(filename):
    records = open(filename, 'r')
    for media in records:
        [app, artist] = [item.strip() for item in media.split(',')]
        if app.lower() == 'soundcloud':
            soundcloud.soundcloud_fetch_media(artist)
        if app.lower() == 'bandcamp':
            bandcamp.bandcamp_fetch_media(artist)
        if app.lower() == 'youtube':
            youtube.youtube_fetch_media(artist)
        if app.lower() == 'vimeo':
            vimeo.vimeo_fetch_media(artist)


if __name__ == "__main__":
    fetch_all('media.txt')
