#!/usr/bin/env python

"""This module contains code to work with vimeo."""

import json
import re
from xml.etree import ElementTree

import requests

from downspout import settings, utils


def vimeo_fetch_metadata(artist):
    video_url = settings.VIMEO_USER_URL.format(artist)
    safe_artist = utils.safe_filename(artist)
    vimeo_response = requests.get(video_url)
    xml = ElementTree.fromstring(vimeo_response.text)
    metadata = utils.tree()

    track_number = 0
    for node in xml.findall('./channel/item'):
        track_number = track_number + 1
        hd_url = None
        sd_url = None

        title = node.find('title').text
        link = node.find('link').text
        link_response = requests.get(link)
        data_config_url = re.findall(
            r'data-config-url=[\'"]?([^\'" >]+)', link_response.text)
        data_config_url = data_config_url[0].replace('&amp;', '&')
        link_response = requests.get(data_config_url)
        link_json = json.loads(link_response.text)

        h264 = link_json['request']['files']['h264']
        try:
            hd_url = h264['hd']['url']
        except:
            pass
        try:
            sd_url = h264['sd']['url']
        except:
            pass
        url = hd_url if hd_url else sd_url

        metadata[artist]['tracks'][title]['url'] = url
        metadata[artist]['tracks'][title]['album'] = ''
        metadata[artist]['tracks'][title]['encoding'] = 'flv'
        metadata[artist]['tracks'][title]['duration'] = None
        metadata[artist]['tracks'][title]['track_number'] = track_number
        metadata[artist]['tracks'][title]['license'] = 'unknown'
        track_filename = str(track_number) + '-' + utils.safe_filename(title) + '.flv'
        metadata[artist]['tracks'][title]['track_filename'] = track_filename
        track_folder = "{0}/{1}".format(
            settings.MEDIA_FOLDER, safe_artist)
        metadata[artist]['tracks'][title]['track_folder'] = track_folder

    return metadata
