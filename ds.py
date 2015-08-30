#!/usr/bin/env python

import os

from downspout import settings, utils, services

# Set the location to your media folder if desired.  The default will save to ./media.
# settings.MEDIA_FOLDER = './downloads'


def fetch_all(filename):
    records = open(filename, 'r')
    for media in records:
        if media[0] == '#':
            continue

        [service, artist] = [item.strip() for item in media.split(',')]
        metadata = utils.metadata_by_artist(service, artist)
        if metadata:
            # utils.dump_metadata(metadata)
            utils.download_from_metadata(metadata, artist, service)


if __name__ == "__main__":
    foo
    print("Running with available services: {}".format(services))
    fetch_all('media.txt')
