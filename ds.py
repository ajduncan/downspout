#!/usr/bin/env python

from collections import defaultdict
import os
import re
import string
import sys
import time

import pafy
import requests
import soundcloud
import taglib

import jsobj


BANDCAMP_FRONT_URL = "http://{0}.bandcamp.com/"
BANDCAMP_ALBUM_URL = "http://{0}.bandcamp.com/album/{1}"

SOUNDCLOUD_CLIENT_ID = "YOUR_CLIENT_ID"
SOUNDCLOUD_FRONT_URL = "https://soundcloud.com"
SOUNDCLOUD_RESOLVE_API = "http://api.soundcloud.com/resolve.json?url={0}&client_id={1}"
SOUNDCLOUD_TRACK_API = "http://api.soundcloud.com/users/{0}/tracks.json?client_id={1}"
SOUNDCLOUD_MEDIA_URL = "http://media.soundcloud.com/stream/{0}"

YOUTUBE_USER_URL = "https://www.youtube.com/user/{0}"
YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v={0}"

MEDIA_FOLDER = "./media"

tree = lambda: defaultdict(tree)


def safe_filename(filename):
    filename.replace(' ', '_')
    valid_characters = "-_.(){0}{1}".format(string.ascii_letters, string.digits)
    safe_name = ''.join(c for c in filename if c in valid_characters)
    return safe_name


# cleaned up
# http://stackoverflow.com/questions/20801034/how-to-measure-download-speed-and-progress-using-requests
def download_file(url, filename):
    try:
        with open(filename, 'wb') as f:
            start = time.clock()
            r = requests.get(url, stream=True)
            total_length = r.headers.get('content-length')
            dl = 0
            if total_length is None: # no content length header
                f.write(r.content)
            else:
                for chunk in r.iter_content(1024):
                    dl += len(chunk)
                    f.write(chunk)
                    done = int(50 * dl / int(total_length))
                    sys.stdout.write("\r[{0}{1}] {2} bps".format('.' * done, ' ' * (50-done), dl//(time.clock() - start)))
                print('')
    except:
        print("Error downloading file: {}".format(sys.exc_info()[0]))

    return (time.clock() - start)


# provided ID3 information, tag the file.
def tagfile(filename, artist, title):
    try:
        f = taglib.File(filename)
        f.tags["ARTIST"] = [artist] 
        f.tags["TITLE"] = [title] 
        f.save()
    except:
        print("Error tagging file: {}".format(sys.exc_info()[0]))


# solution cheerfully obtained from https://github.com/iheanyi/bandcamp-dl/blob/master/bandcamp-dl/Bandcamp.py#L69
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
    url = BANDCAMP_FRONT_URL.format(artist)
    media = tree()
    safe_user = safe_filename(artist)

    print('Checking URL for albums: {}'.format(url))
    bandcrap = requests.get(url)

    albums = re.findall(r'href=[\'"]?\/album\/{1}([^\'" >]+)', bandcrap.text)
    for album in albums:
        print("Procuring the {} album for your listening enjoyment.".format(album))
        album_url = BANDCAMP_ALBUM_URL.format(artist, album)
        bandcamp_album_response = requests.get(album_url)
        album_block = bandcamp_get_album_block(bandcamp_album_response)
        embed_block = bandcamp_get_embed_block(bandcamp_album_response)

        album_title = embed_block['EmbedData']['album_title']
        media[artist][album_title]['tracks'] = []
        media[artist][album_title]['date'] = album_block['TralbumData']['album_release_date'].split()[2]

        for track in album_block['TralbumData']['trackinfo']:
            media[artist][album_title]['tracks'].append(bandcamp_get_track_data(track))

    safe_user = safe_filename(artist)
    for index in media:
        print("Artist: {}".format(index))
        for album in media[index]:
            print("Album: {}".format(album))
            safe_album = safe_filename(album)

            for track in media[index][album]['tracks']:
                # this is where the magic happens!
                safe_track = '' + track['track'] + '-' + safe_filename(track['title']) + '.mp3'
                track_folder = "{0}/{1}/{2}".format(MEDIA_FOLDER, safe_user, safe_album)
                print("Saving {0} from {1} to {2}".format(safe_track, track['url'], track_folder))
                try:
                    os.makedirs(track_folder, exist_ok=True)
                    filename = "{0}/{1}".format(track_folder, safe_track)
                    if not os.path.isfile(filename):
                        elapsed = download_file(track['url'], filename)
                        tagfile(filename, artist, track['title'])
                        print("Download completed in: {}".format(round(elapsed, 2)))
                    else:
                        print("Already downloaded: {}".format(filename))
                except:
                    pass
                print('')

    print('')


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
        print("Downloading {2} tracks from {0}'s (User ID: {1}) soundcloud account.".format(
            user, user_id, track_count))
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
            media[user_id][track['title']] = SOUNDCLOUD_MEDIA_URL.format(stream_id)
        except:
            pass

    safe_user = safe_filename(user)
    for track in media[user_id].keys():
        safe_track = '' + safe_filename(track) + '.mp3'
        track_folder = "{0}/{1}".format(MEDIA_FOLDER, safe_user)
        print("Saving {0} from {1} to {2}".format(safe_track, media[user_id][track], track_folder))
        try:
            os.makedirs(track_folder, exist_ok=True)
            filename = "{0}/{1}".format(track_folder, safe_track)
            if not os.path.isfile(filename):
                elapsed = download_file(media[user_id][track], filename)
                tagfile(filename, user, track)
                print("Download completed in: {}".format(round(elapsed, 2)))
            else:
                print("Already downloaded: {}".format(filename))
        except:
            pass
        print('')


# fetch all of a user's uploaded videos ...
def youtube_fetch_media(artist):
    video_url = YOUTUBE_USER_URL.format(artist) + '/videos'
    yt_response = requests.get(video_url)
    videos = set(re.findall(r'href="\/watch\?v=([^&|"]+)', yt_response.text))
    for link in videos:
        video = pafy.new(YOUTUBE_VIDEO_URL.format(link))
        print("Video: {}".format(video.title))


    print('')


def fetch_all(filename):
    records = open(filename, 'r')
    for media in records:
        [app, artist] = [item.strip() for item in media.split(',')]
        if app.lower() == 'soundcloud':
            soundcloud_fetch_media('{0}/{1}'.format(SOUNDCLOUD_FRONT_URL, artist))
        if app.lower() == 'bandcamp':
            bandcamp_fetch_media(artist)
        if app.lower() == 'youtube':
            youtube_fetch_media(artist)


if __name__ == "__main__":
    fetch_all('media.txt')
