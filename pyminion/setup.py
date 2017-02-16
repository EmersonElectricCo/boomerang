#!/usr/bin/env python

from distutils.core import setup

setup(name='pyminion',
      version='2.0',
      description='Python bindings to the API for the minion component of Boomerang',
      author='Timothy Lemm',
      author_email='timothy.lemm@emerson.com',
      url='https://github.com/EmersonElectricCo/boomerang',
      packages=['pyminion'],
	  install_requires=['requests']
      )
