#!/usr/bin/env python

"""This module contains code to work with soundcloud."""

from collections import defaultdict
import json
import re

import requests

from downspout.settings import *
from downspout.utils import get_file, safe_filename

tree = lambda: defaultdict(tree)


# fetch all artist media at url, which has
# the format https://soundcloud.com/username
def soundcloud_fetch_media(url):
    api = SOUNDCLOUD_RESOLVE_API.format(url, SOUNDCLOUD_CLIENT_ID)
    media = tree()

    resolver = requests.get(api)
    try:
        user = resolver.json()['username']
        user_id = resolver.json()['id']
        track_count = int(resolver.json()['track_count'])
        track_api = SOUNDCLOUD_TRACK_API.format(user_id, SOUNDCLOUD_CLIENT_ID)
        tracks = requests.get(track_api).json()
    except:
        pass

    for track in tracks:
        try:
            waveform_url = track['waveform_url']
            regex = re.compile("\/([a-zA-Z0-9]+)_")
            r = regex.search(waveform_url)
            stream_id = r.groups()[0]
            media[user_id][
                track['title']] = SOUNDCLOUD_MEDIA_URL.format(stream_id)
        except:
            pass

    safe_user = safe_filename(user)
    for track in media[user_id].keys():
        safe_track = '' + safe_filename(track) + '.mp3'
        track_folder = "{0}/{1}".format(MEDIA_FOLDER, safe_user)

        try:
            get_file(
                track_folder, safe_track, user, track, media[user_id][track])
        except:
            pass
        print('')

    print('')
