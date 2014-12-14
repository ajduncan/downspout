#!/usr/bin/env python

"""This module contains code to work with youtube."""

import re

import pafy
import requests

from downspout.settings import *
from downspout.utils import get_file, safe_filename


# fetch all of a user's uploaded videos ...
def youtube_fetch_media(artist):
    video_url = YOUTUBE_USER_URL.format(artist) + '/videos'
    yt_response = requests.get(video_url)
    videos = set(re.findall(r'href="\/watch\?v=([^&|"]+)', yt_response.text))
    safe_user = safe_filename(artist)
    for link in videos:
        video = pafy.new(YOUTUBE_VIDEO_URL.format(link))
        audiostream = video.getbestaudio()
        safe_track = '' + \
            safe_filename(audiostream.title) + '.' + audiostream.extension
        track_folder = "{0}/{1}".format(MEDIA_FOLDER, safe_user)
        try:
            get_file(
                track_folder, safe_track, artist, video.title, audiostream.url)
        except:
            pass

    print('')
