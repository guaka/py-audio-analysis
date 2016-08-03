#! /usr/bin/env python

version = "0.1"

from distutils.core import setup
import sys
import os.path
import time

if sys.version < '2.3':
	print "You need at least Python 2.3.0"
	exit

desc = "Find structure in musical pieces"



def adorno_setup():
	setup(name = "adorno",
		  version = version,
		  author = "Guaka",
		  author_email = "guaka AT 303 DOT nu",
		  url = "http://industree.org/guaka/adorno/",
		  download_url = "http://industree.org/guaka/download/",
		  description = desc,
		  long_description = desc,
		  packages = ['adorno'],

		  classifiers = ['Development Status :: 4 - Beta',
						 'Environment :: GUI',
						 'Intended Audience :: End Users/Desktop',
						 'Intended Audience :: Developers',
						 'License :: OSI Approved :: GNU General Public Licensed',
						 'Operating System :: MacOS :: MacOS X',
						 'Operating System :: POSIX',
						 'Programming Language :: Python',
						 ],
		  )

if __name__ == "__main__":
	adorno_setup()


