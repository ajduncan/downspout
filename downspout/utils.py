#!/usr/bin/env python

"""Utilities for downloading, saving and tagging files from the cloud."""

from collections import defaultdict
import importlib
import json
import os
import sys
import string
import time

import requests
import taglib

from downspout import settings

tree = lambda: defaultdict(tree)


def safe_filename(filename):
    filename = filename.replace(' ', '_')
    valid_characters = "-_.(){0}{1}".format(string.ascii_letters,
                                            string.digits)
    safe_name = ''.join(c for c in filename if c in valid_characters)
    return safe_name


# cleaned up
# http://stackoverflow.com/questions/20801034/how-to-measure-download-speed-and-progress-using-requests
def get_file(track_folder, safe_track, artist, title, url):
    try:
        os.makedirs(track_folder, exist_ok=True)
        filename = "{0}/{1}".format(track_folder, safe_track)
        if not os.path.isfile(filename):
            short_url = (url[:50] + ' ...') if len(url) > 50 else url
            print("Saving {0} from {1} to {2}".format(
                safe_track, short_url, track_folder))

            with open(filename, 'wb') as f:
                start = time.clock()
                r = requests.get(url, stream=True)
                total_length = r.headers.get('content-length')
                dl = 0
                if total_length is None:  # no content length header
                    f.write(r.content)
                else:
                    for chunk in r.iter_content(1024):
                        dl += len(chunk)
                        f.write(chunk)
                        done = int(50 * dl / int(total_length))
                        sys.stdout.write("\r[{0}{1}] {2} bps".format(
                            '.' * done, ' ' * (50 - done), dl // (time.clock() - start)))
                    print('')
            elapsed = time.clock() - start
            tagfile(filename, artist, track['title'])
            print("Download completed in: {}".format(round(elapsed, 2)))
        else:
            print("Already downloaded: {}".format(filename))
    except:
        pass
    print('')

    return elapsed


# provided ID3 information, tag the file.
def tagfile(filename, artist, title):
    try:
        f = taglib.File(filename)
        f.tags["ARTIST"] = [artist]
        f.tags["TITLE"] = [title]
        f.save()
    except:
        print("Error tagging file: {}".format(sys.exc_info()[0]))


def download_from_metadata(metadata, artist, service):
    safe_artist = safe_filename(artist)

    for track_title in metadata[artist]['tracks']:
        track_url = metadata[artist]['tracks'][track_title]['url']
        track_album = metadata[artist]['tracks'][track_title]['album']
        track_extension = metadata[artist]['tracks'][track_title]['encoding']
        track_number = metadata[artist]['tracks'][track_title]['track_number']
        track_number = str(track_number) + '-' if track_number != -1 else ''
        safe_album = safe_filename(track_album)
        safe_track = safe_filename(track_title) + '.' + track_extension
        safe_track = track_number + safe_track
        track_folder = "{0}/{1}/{2}".format(
            settings.MEDIA_FOLDER, safe_artist, safe_album)

        try:
            get_file(
                track_folder, safe_track, artist, track_title, track_url)
        except:
            pass
        print('')

    print('')


# print/dump metadata
def dump_metadata(metadata):
    print(json.dumps(metadata, sort_keys=True, indent=4))


# provided artist and service, return metadata about the artists tracks, albums, etc.
def metadata_by_artist(service, artist):
    try:
        module = importlib.import_module('downspout.' + service)
    except ImportError:
        print("Service unknown: '{}'".format(service))
        return None

    fetch_metadata = getattr(module, service + '_fetch_metadata', lambda: None)
    return fetch_metadata(artist)
