# downspout #

[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/ajduncan/downspout?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Where fair use meets fu.  Capture cloud based media for offline merriment.

[![Build Status](https://travis-ci.org/ajduncan/downspout.svg?branch=master)](https://travis-ci.org/ajduncan/downspout)

## Installing ##

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
