#! /usr/bin/env python

from distutils.core import setup

from distutils.sysconfig import get_config_vars

import os
import sys
from glob import glob
from os.path import isfile, join, abspath

try:
	import scipy
except ImportError:
	print """SciPy is required

	check out www.scipy.org
	"""


if not os.name == 'posix':
	print "Unsupported operating system:", os.name
	sys.exit()



scriptfiles = [f for f in glob('scripts/*') if f[-1] != "~" and isfile(f)]
palette_files = filter(isfile, glob(join(abspath(""), 'FfAA/gist_palettes/*')))

install_dir = join(get_config_vars()["DESTLIB"], "site-packages", "FfAA")

#TODO:
# scriptfiles in MANIFEST

setup(name = 'FfAA',
	  version = '0.1-alpha0',
	  description = 'Python Framework for Audio Analysis',
	  author = 'Kasper Souren',
	  author_email = 'Kasper.Souren@ircam.fr',
	  url = 'http://www.ircam.fr/anasyn/souren/',
	  packages = ['FfAA', 'FfAA.genprog', 'FfAA.descriptors'],
	  scripts = scriptfiles,
	  data_files = [(join(install_dir, "gist_palettes"), palette_files)],
	  long_description = '''
	  Python Framework for Audio Analysis
	  ''')
