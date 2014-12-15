#!/usr/bin/env python

from distutils.core import setup

requires = [
	'Pafy==0.3.66',
	'fudge==1.0.3',
	'pytaglib==0.4.1',
	'requests==2.5.0',
	'simplejson==3.6.5',
	'slimit==0.8.1',
]


setup(name='downspout',
      version='0.0.1',
      description='Capture cloud based media for offline merriment.',
      license='MIT',
      author='Andy Duncan',
      author_email='ajduncan@gmail.com',
      url='https://github.com/ajduncan/downspout/',
      install_requires=requires,
     )
