#!/usr/bin/env python

"""This module contains code to work with bandcamp."""

import re

import jsobj
import requests

from bandcamp_dl.bandcamp import Bandcamp

from downspout import settings, utils
from downspout.utils import get_file, safe_filename


def bandcamp_get_track_data(track):
    new_track = {}
    new_track['url'] = track['url']
    new_track['duration'] = track['duration']
    new_track['track'] = track['track']
    new_track['title'] = track['title']

    return new_track


# fetch all artist metadata by album at url,
# which has the format http://<artist>.bandcamp.com/
def bandcamp_fetch_metadata(artist):
    url = settings.BANDCAMP_FRONT_URL.format(artist)
    safe_artist = utils.safe_filename(artist)
    media = utils.tree()
    metadata = utils.tree()
    metadata[artist]['services']['bandcamp'] = url
    
    bandcrap = requests.get(url)
    albums = re.findall(r'href=[\'"]?\/album\/{1}([^\'" >]+)', bandcrap.text)
    for album in albums:
        album_url = settings.BANDCAMP_ALBUM_URL.format(artist, album)
        album = Bandcamp().parse(album_url)
        album_title = album['title']
        media[artist][album_title] = {}
        media[artist][album_title]['tracks'] = []
        media[artist][album_title]['date'] = album['date']

        for track in album['tracks']:
            media[artist][album_title]['tracks'].append(
                bandcamp_get_track_data(track)
            )

    for index in media:
        for album in media[index]:
            safe_album = utils.safe_filename(album)
            for track in media[index][album]['tracks']:
                metadata[artist]['tracks'][track['title']]['url'] = 'http:' + track['url']
                print('Got track: %s', track)
                metadata[artist]['tracks'][track['title']]['url'] = track['url']
                metadata[artist]['tracks'][track['title']]['album'] = album
                metadata[artist]['tracks'][track['title']]['encoding'] = 'mp3'
                metadata[artist]['tracks'][track['title']]['duration'] = track['duration']
                metadata[artist]['tracks'][track['title']]['track_number'] = track['track'] if 'track' in track else -1
                metadata[artist]['tracks'][track['title']]['license'] = 'unknown'
                track_filename = track['track'] + '-' if 'track' in track else ''
                track_filename = track_filename + utils.safe_filename(track['title']) + '.mp3'
                metadata[artist]['tracks'][track['title']]['track_filename'] = track_filename
                track_folder = "{0}/{1}/{2}".format(
                    settings.MEDIA_FOLDER, safe_artist, safe_album)
                metadata[artist]['tracks'][track['title']]['track_folder'] = track_folder

    return metadata
