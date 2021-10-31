#!/usr/bin/env python

from setuptools import setup

install_requires = [
  'Pafy==0.3.66',
  'fudge==1.0.3',
  'requests>=2.20.0',
  'simplejson==3.6.5',
  'slimit==0.8.1',
  'stagger',
]

dependency_links = [
  'git://github.com/ajduncan/stagger.git@master#egg=stagger',
]


setup(name='downspout',
      version='v0.0.5',
      description='Capture cloud based media for offline merriment.',
      license='MIT',
      author='Andy Duncan',
      author_email='ajduncan@gmail.com',
      url='https://github.com/ajduncan/downspout/',
      install_requires=install_requires,
      dependency_links=dependency_links,
      test_suite='tests.runtests'
     )
