#!/usr/bin/env ipython

import mmap
import sys
import os

from Numeric import *
import MLab
import RandomArray

import Image
from scipy import pilutil, io

from qt import *


# from PyGist's Mplot.py
def gist_palettes(get_them = False):
	import scipy
	import os, glob
	#direc = os.environ['GISTPATH']
	direc = "gist_palettes/"
	files = glob.glob1(direc, "*.gp")
	lengths = map(len, files)

	if get_them:
		gist = {}
	else:
		print "Available palettes..."
		print "=====================\n"

	if files:
		maxlen = scipy.amax(lengths)
	
	for file in files:
		k = 0
		fn = os.path.join(direc, file)
		fid = open(fn)		  
		if get_them:
			gist[file[:-3]] = gist_load(fn)
		else:
			print file[:-3] + ' '*(maxlen-len(file[:-3])-3) + ' --- ',
			while 1:
				line = fid.readline()
				if line[0] != '#':
					fid.close()
					if k == 0:
						print
					break
				if k > 0:
					print ' '*(maxlen+3) + line[1:-1]
				else:
					print line[1:-1]
				k = k + 1
	if get_them:
		return gist

def gist_load(fn):
	import string

	f = open(fn)
	not_done = True
	while not_done:
		p = f.tell()
		s = f.readline()
		ss = string.split(s)
		if len(ss) == 3 and reduce(lambda b, c: b and c in string.digits, "".join(ss)):
			f.seek(p)
			arr = io.read_array(f, atype = 'b')
			not_done = False
	return arr
			
palettes = gist_palettes(get_them = True)


def normalize_rows(arr):
	min = zeros(len(arr), Float32)
	max = zeros(len(arr), Float32)
	dif = zeros(len(arr), Float32)
	for r in arange(len(arr)):
		max[r] = arr[r, argmax(arr[r])]
		min[r] = arr[r, argmin(arr[r])]
		dif[r] = (max[r] - min[r]) or 1
	return (arr - outerproduct(min, [1] * shape(arr)[1])) / outerproduct(dif, [1] * shape(arr)[1])

a = arange(0, 1., 1/256.)
palfuncs = lambda f,g,h: transpose(normalize_rows(concatenate((f(a)[NewAxis,:],
															   g(a)[NewAxis,:],
															   h(a)[NewAxis,:]))) * 255).astype('b')

id = lambda x: x

p1 = palfuncs(lambda x:25 * sqrt(x) + 0.8*x + (x+1)*(0.4*x-1),
			  lambda x: 1.01 * x*x*x - 2.1 * x*x + 1.4 * x,
			  id)

palettes["gray"] = palfuncs(id, id, id)
palettes["brownish"] = palfuncs(sin, exp, lambda x: x*x*x)

palettes["purplish"] = palfuncs(sin, exp, lambda x: sqrt(x))
palettes["greenish"] = palfuncs(sin,
								lambda x: 1.01 * x*x*x - 2.1 * x*x + 1.4 * x,
								lambda x: sqrt(x))

palettes["matlabtest"] = palfuncs(lambda x: x,
								  lambda x: pow(x * (1-x), 2),
								  lambda x: 1 - x)



class QImagePlot(QWidget):
	def __init__(self, parent, *args):
		QWidget.__init__(self, parent, *args)
		self.array = None
		self.image = None

		self.temp = "/tmp/test.png"

		self.setArray(array([[0,0], [0,0]]))
		# pilutil.fromimage ..
		
	def setArray(self, arr, palette = palettes["brownish"]):
		self.array = arr

		# if no_scaling: #for subplots and stuff like that...
		#  im = pilutil.toimage(MLab.flipud(arr), pal = palette, cmin = 0., cmax = 1.)
		self.image = pilutil.toimage(MLab.flipud(arr), pal = palette)
		self.afterResize()

	def afterResize(self):
		s = self.size()
		size = s.width(), s.height()

		print size

		if self.image:
			im = self.image.resize(size)
			im.save(self.temp)

		pixmap = QPixmap(self.temp)
		self.setPaletteBackgroundPixmap(pixmap)

	def resizeEvent(self, e):
		self.afterResize()

class QImagePlotCached(QImagePlot):
	def __init__(self, parent, filename = None, arr = None, *args):
		QWidget.__init__(self, parent, *args)
		self.array = self.image = None
		self.filename = filename

		self.temp = "/tmp/test.png"
		if not arr == None:
			self.setArray(arr) 
		elif filename and os.path.exists(filename):
			self.setImage(filename)
		else:
			self.setArray(array([[0,0], [0,0]]))

	def setImage(self, filename):
		self.image = Image.open(filename)
		self.array = pilutil.fromimage(self.image)
		self.afterResize()

def testRandom(nx, ny):
	return RandomArray.random((nx, ny))

def testLinearX(nx, ny):
	return repeat(arange(nx, typecode = Float32)[:, NewAxis], ny, -1)

def testLinearY(nx, ny):
	return repeat(arange(ny, typecode = Float32)[NewAxis, :], nx, 0)


def testArray(i):
	x = y = i
	return (testLinearX(x, y) +
			testLinearY(x, y))
#testRandom(x, y) * x / 5)


if __name__ == '__main__':
	app = QApplication(sys.argv)

	w = QMainWindow()
	t = QImagePlotCached(w)
	t.show()
	t.resize(300, 400)
	w.show()

	t.setArray(testLinearY(200, 20) + testRandom(200, 20))

	app.setMainWidget(w)
	app.exec_loop()
