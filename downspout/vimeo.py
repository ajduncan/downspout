#!/usr/bin/env python

"""This module contains code to work with soundcloud."""

import json
import re
from xml.etree import ElementTree

import requests

from downspout.settings import *
from downspout.utils import get_file, safe_filename


def vimeo_fetch_media(artist):
    video_url = VIMEO_USER_URL.format(artist)
    vimeo_response = requests.get(video_url)
    xml = ElementTree.fromstring(vimeo_response.text)
    safe_user = safe_filename(artist)
    for node in xml.findall('./channel/item'):
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
        safe_track = '' + safe_filename(title) + '.flv'
        track_folder = "{0}/{1}".format(MEDIA_FOLDER, safe_user)
        try:
            get_file(track_folder, safe_track, artist, title, url)
        except:
            pass

    print('')
