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
import stagger

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
def get_file(track_folder, track_filename, artist, title, url):
    try:
        os.makedirs(track_folder, exist_ok=True)
        filename = "{0}/{1}".format(track_folder, track_filename)
        if not os.path.isfile(filename):
            short_url = (url[:50] + ' ...') if len(url) > 50 else url
            print("Saving {0} from {1} to {2}".format(
                track_filename, short_url, track_folder))

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
            tagfile(filename, artist, title)
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
        tag = stagger.Tag24() # read_tag(filename)
        tag.artist = artist
        tag.title = title 
        tag.write(filename)
    except:
        print("Error tagging file: {}".format(sys.exc_info()[0]))


def download_from_metadata(metadata, artist, service):
    safe_artist = safe_filename(artist)

    for track_title in metadata[artist]['tracks']:
        track_url = metadata[artist]['tracks'][track_title]['url']
        track_album = metadata[artist]['tracks'][track_title]['album']
        track_extension = metadata[artist]['tracks'][track_title]['encoding']
        track_number = metadata[artist]['tracks'][track_title]['track_number']
        track_folder = metadata[artist]['tracks'][track_title]['track_folder']
        track_filename = metadata[artist]['tracks'][track_title]['track_filename']

        try:
            get_file(
                track_folder, track_filename, artist, track_title, track_url)
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


# fetch all media for artist from service
def fetch(service, artist):
    metadata = metadata_by_artist(service, artist)
    if metadata:
        download_from_metadata(metadata, artist, service)
        return metadata
    else:
        return False


# fetch everything from file
def fetch_all(filename):
    records = open(filename, 'r')
    for media in records:
        [service, artist] = [item.strip() for item in media.split(',')]
        metadata = metadata_by_artist(service, artist)
        if metadata:
            # dump_metadata(metadata)
            download_from_metadata(metadata, artist, service)

    return True
