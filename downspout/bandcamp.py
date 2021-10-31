#!/usr/bin/env python

"""This module contains code to work with bandcamp."""

import re

import jsobj
import requests

from downspout import settings, utils
from downspout.utils import get_file, safe_filename


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
        bandcamp_album_response = requests.get(album_url)
        album_block = bandcamp_get_album_block(bandcamp_album_response)
        print('Got album block: {}'.format(album_block))
        urls_block = bandcamp_get_stream_urls(bandcamp_album_response)
        embed_block = bandcamp_get_embed_block(bandcamp_album_response)

        album_title = embed_block['EmbedData']['album_title']
        media[artist][album_title]['tracks'] = []
        media[artist][album_title]['date'] = album_block[
            'TralbumData']['album_release_date'].split()[2]

        for track in album_block['TralbumData']['trackinfo']:
            media[artist][album_title]['tracks'].append(
                bandcamp_get_track_data(track))
        exit
    for index in media:
        for album in media[index]:
            safe_album = utils.safe_filename(album)
            for track in media[index][album]['tracks']:
                metadata[artist]['tracks'][track['title']]['url'] = 'http:' + track['url']
                print('Got track: %s', track)
                # metadata[artist]['tracks'][track['title']]['url'] = track['url']
                metadata[artist]['tracks'][track['title']]['album'] = album
                metadata[artist]['tracks'][track['title']]['encoding'] = 'mp3'
                metadata[artist]['tracks'][track['title']]['duration'] = track['duration']
                metadata[artist]['tracks'][track['title']]['track_number'] = track['track_num'] if 'track_num' in track else -1
                metadata[artist]['tracks'][track['title']]['license'] = 'unknown'
                track_filename = track['track_num'] + '-' if 'track_num' in track else ''
                track_filename = track_filename + utils.safe_filename(track['title']) + '.mp3'
                metadata[artist]['tracks'][track['title']]['track_filename'] = track_filename
                track_folder = "{0}/{1}/{2}".format(
                    settings.MEDIA_FOLDER, safe_artist, safe_album)
                metadata[artist]['tracks'][track['title']]['track_folder'] = track_folder

    return metadata
