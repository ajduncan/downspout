#!/usr/bin/env python

"""This module contains code to work with bandcamp."""

from collections import defaultdict
import re

import jsobj
import requests

from downspout import settings
from downspout.utils import get_file, safe_filename

tree = lambda: defaultdict(tree)


# solution cheerfully obtained from
# https://github.com/iheanyi/bandcamp-dl/blob/master/bandcamp-dl/Bandcamp.py#L69
def bandcamp_get_album_block(response):
    block = response.text.split('var TralbumData = ')
    block = block[1]
    block = block.partition("};")[0] + "};"
    block = jsobj.read_js_object("var TralbumData = {}".format(block))
    return block


def bandcamp_get_embed_block(response):
    block = response.text.split("var EmbedData = ")

    block = block[1]
    block = block.split("};")[0] + "};"
    block = jsobj.read_js_object("var EmbedData = {}".format(block))

    return block


def bandcamp_get_track_data(track):
    new_track = {}
    if 'mp3-128' in track['file']:
        new_track['url'] = track['file']['mp3-128']
    else:
        new_track['url'] = None

    new_track['duration'] = track['duration']
    new_track['track'] = track['track_num']
    new_track['title'] = track['title']

    return new_track


# fetch all artist media by album at url,
# which has the format http://<artist>.bandcamp.com/
def bandcamp_fetch_media(artist):
    url = settings.BANDCAMP_FRONT_URL.format(artist)
    media = tree()
    safe_user = safe_filename(artist)
    bandcrap = requests.get(url)

    albums = re.findall(r'href=[\'"]?\/album\/{1}([^\'" >]+)', bandcrap.text)
    for album in albums:
        album_url = settings.BANDCAMP_ALBUM_URL.format(artist, album)
        bandcamp_album_response = requests.get(album_url)
        album_block = bandcamp_get_album_block(bandcamp_album_response)
        embed_block = bandcamp_get_embed_block(bandcamp_album_response)

        album_title = embed_block['EmbedData']['album_title']
        media[artist][album_title]['tracks'] = []
        media[artist][album_title]['date'] = album_block[
            'TralbumData']['album_release_date'].split()[2]

        for track in album_block['TralbumData']['trackinfo']:
            media[artist][album_title]['tracks'].append(
                bandcamp_get_track_data(track))

    safe_user = safe_filename(artist)
    for index in media:
        for album in media[index]:
            safe_album = safe_filename(album)

            for track in media[index][album]['tracks']:
                safe_track = '' + \
                    track['track'] + '-' + \
                    safe_filename(track['title']) + '.mp3'
                track_folder = "{0}/{1}/{2}".format(
                    settings.MEDIA_FOLDER, safe_user, safe_album)
                try:
                    get_file(
                        track_folder, safe_track, artist, track['title'], track['url'])
                except:
                    pass
                print('')

    print('')
