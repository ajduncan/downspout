#!/usr/bin/env python

"""Utilities for downloading, saving and tagging files from the cloud."""

import os
import sys
import string
import time

import requests
import taglib


def safe_filename(filename):
    filename.replace(' ', '_')
    valid_characters = "-_.(){0}{1}".format(string.ascii_letters,
                                            string.digits)
    safe_name = ''.join(c for c in filename if c in valid_characters)
    return safe_name


# cleaned up
# http://stackoverflow.com/questions/20801034/how-to-measure-download-speed-and-progress-using-requests
def get_file(track_folder, safe_track, artist, title, url):
    short_url = (url[:50] + ' ...') if len(url) > 50 else url
    print("Saving {0} from {1} to {2}".format(
        safe_track, short_url, track_folder))

    try:
        os.makedirs(track_folder, exist_ok=True)
        filename = "{0}/{1}".format(track_folder, safe_track)
        if not os.path.isfile(filename):
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
