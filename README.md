# downspout #

Where fair use meets fu.  Capture cloud based media for offline merriment.

[![Build Status](https://travis-ci.org/ajduncan/downspout.svg?branch=master)](https://travis-ci.org/ajduncan/downspout)

## Installing ##

    You need taglib to use ID3 tagging with pytaglib.  See:
    https://github.com/taglib/taglib/blob/master/INSTALL

	OSX/Linux:

	$ virtualenv -p python3 .env
	$ source .env/bin/activate
	$ (.env) pip install -r requirements.txt

## Running ##

	Add some lines to media.txt in the format:
	
	service,artist

	Where service may be soundcloud, bandcamp, youtube or vimeo.

	$ (.env) python ds.py

## Testing ##

	$ (.env) ./runtests.sh

## Disclaimer ##

	Use at your own risk and according to the terms of service for these services.
	This is only a proof of concept.
