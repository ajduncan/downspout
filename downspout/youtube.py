#!/usr/bin/env python

"""This module contains code to work with youtube."""

import re

import pafy
import requests

from downspout import settings, utils


# fetch all of a user's uploaded videos ...
def youtube_fetch_metadata(artist):
    video_url = settings.YOUTUBE_USER_URL.format(artist) + '/videos'
    safe_artist = utils.safe_filename(artist)
    yt_response = requests.get(video_url)
    videos = set(re.findall(r'href="\/watch\?v=([^&|"]+)', yt_response.text))
    metadata = utils.tree()

    for link in videos:
        video = pafy.new(settings.YOUTUBE_VIDEO_URL.format(link))
        audiostream = video.getbestaudio()

        # note, artist here may not be author (video.author) ...
        # also audiostream.title ?
        metadata[artist]['tracks'][video.title]['url'] = audiostream.url
        metadata[artist]['tracks'][video.title]['album'] = ''
        metadata[artist]['tracks'][video.title]['encoding'] = audiostream.extension
        metadata[artist]['tracks'][video.title]['duration'] = video.duration
        metadata[artist]['tracks'][video.title]['track_number'] = ''
        metadata[artist]['tracks'][video.title]['license'] = 'unknown'
        track_filename = utils.safe_filename(video.title) + '.' + audiostream.extension
        metadata[artist]['tracks'][video.title]['track_filename'] = track_filename
        track_folder = "{0}/{1}".format(
            settings.MEDIA_FOLDER, safe_artist)
        metadata[artist]['tracks'][video.title]['track_folder'] = track_folder

    return metadata
