#!/usr/bin/env python

"""This module contains code to work with soundcloud."""

import json
import re

import requests

from downspout import settings, utils


# fetch all artist media at url, which has
# the format https://soundcloud.com/username
def soundcloud_fetch_metadata(artist):
    url = '{0}/{1}'.format(settings.SOUNDCLOUD_FRONT_URL, artist)
    safe_artist = utils.safe_filename(artist)
    api = settings.SOUNDCLOUD_RESOLVE_API.format(url, settings.SOUNDCLOUD_CLIENT_ID)
    metadata = utils.tree()

    resolver = requests.get(api)
    try:
        user = resolver.json()['username']
        user_id = resolver.json()['id']
        track_count = int(resolver.json()['track_count'])
        track_api = settings.SOUNDCLOUD_TRACK_API.format(user_id, settings.SOUNDCLOUD_CLIENT_ID)
        tracks = requests.get(track_api).json()
    except:
        pass

    track_number = 0
    for track in tracks:
        track_number = track_number + 1
        try:
            waveform_url = track['waveform_url']
            regex = re.compile("\/([a-zA-Z0-9]+)_")
            r = regex.search(waveform_url)
            stream_id = r.groups()[0]

            metadata[artist]['tracks'][track['title']]['url'] = settings.SOUNDCLOUD_MEDIA_URL.format(stream_id)
            metadata[artist]['tracks'][track['title']]['album'] = ''
            metadata[artist]['tracks'][track['title']]['encoding'] = 'mp3'
            metadata[artist]['tracks'][track['title']]['duration'] = None
            metadata[artist]['tracks'][track['title']]['track_number'] = track_number
            metadata[artist]['tracks'][track['title']]['license'] = 'unknown'
            track_filename = track['track_num'] + '-' if 'track_num' in track else ''
            track_filename = track_filename + utils.safe_filename(track['title']) + '.mp3'
            metadata[artist]['tracks'][track['title']]['track_filename'] = track_filename
            track_folder = "{0}/{1}".format(
                settings.MEDIA_FOLDER, safe_artist)
            metadata[artist]['tracks'][track['title']]['track_folder'] = track_folder

        except:
            pass

    return metadata
