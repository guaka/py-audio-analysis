#!/usr/bin/env ipython


"""
QImagePlot.py


TODO
* find a better method than the tmp file: mmap or CStringIO
* palettes: naming, leave gist stuff like this?
* legend: now done as a subclass of QwtImagePlot, needs improvements
* zoom stuff: not perfect on pixel-scale?

"""



import mmap
import sys

from Numeric import *
import MLab
import RandomArray

import Image
from scipy import pilutil, io

from qt import *
from qwt import *


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
	def __init__(self, *args):
		QWidget.__init__(self, *args)
		self.array = None
		self.image = None

	def setArray(self, arr, palette = palettes["brownish"]):
		self.array = arr

		# if no_scaling: #for subplots and stuff like that...
		#  im = pilutil.toimage(MLab.flipud(arr), pal = palette, cmin = 0., cmax = 1.)
		self.image = pilutil.toimage(MLab.flipud(arr), pal = palette)
		self.afterResize()

	def afterResize(self):
		s = self.size()
		size = s.width(), s.height()
	
		im = self.image.resize(size)
		im.save("/tmp/test.png")

		pixmap = QPixmap("/tmp/test.png")
		self.setPaletteBackgroundPixmap(pixmap)

	def resizeEvent(self, e):
		self.afterResize()


class QwtImagePlot(QwtPlot):
	def __init__(self, *args):
		apply(QwtPlot.__init__, (self,) + args)
		# make a QwtPlot widget
		#self.setTitle('A Simple PyQwt Plot Demonstration')
		#self.setAutoLegend(1)
		#self.setLegendPos(Qwt.Right)

		self.rescale_on_zoom = False
		self.legend = None

		if False:
			# set axis titles
			self.setAxisTitle(QwtPlot.xBottom, 'x -->')
			self.setAxisTitle(QwtPlot.yLeft, 'y -->')

			# insert a few curves
			cSin = self.insertCurve('y = sin(x)')
			cCos = self.insertCurve('y = cos(x)')
			# set curve styles
			self.setCurvePen(cSin, QPen(Qt.red))
			self.setCurvePen(cCos, QPen(Qt.blue))
			# calculate 3 NumPy arrays
			x = arrayrange(0.0, 10.0, 0.1)
			y = sin(x)
			z = cos(x)
			# copy the data
			self.setCurveData(cSin, x, y)
			self.setCurveData(cCos, x, z)
			# insert a horizontal marker at y = 0
			mY = self.insertLineMarker('y = 0', QwtPlot.yLeft)
			self.setMarkerYPos(mY, 0.0)
			# insert a vertical marker at x = 2 pi
			mX = self.insertLineMarker('x = 2 pi', QwtPlot.xBottom)
			self.setMarkerXPos(mX, 2*pi)

		self.array = None
		self.image = None
		self.palette = None
		
	def setArray(self, arr, palette = None, axis_x_max = None, axis_y_max = None):
		self.array = arr
		self.palette = palette or palettes["brownish"]

		s = shape(arr)
		axis_y_max = axis_y_max or s[0]
		axis_x_max = axis_x_max or s[1]

		self.setAxisScale(QwtPlot.xBottom, 0, axis_x_max)
		self.setAxisScale(QwtPlot.yLeft, 0, axis_y_max)
		self.replot()
		
		# if no_scaling: #for subplots and stuff like that...
		#  im = pilutil.toimage(MLab.flipud(arr), pal = palette, cmin = 0., cmax = 1.)
		self.image = pilutil.toimage(MLab.flipud(arr), pal = self.palette)
		if hasattr(self, "image_unzoomed"):
			self.image_unzoomed = self.image
		self.doPlotImage()

		if self.legend:
			self.legend.setImagePlot(self)

	def setPalette(self, palette):
		self.palette = palette
		if self.array:
			self.image = pilutil.toimage(MLab.flipud(self.array), pal = palette)
			self.doPlotImage()
		if self.legend:
			self.legend.setImagePlot(self)

	def doPlotImage(self):
		if self.image:
			s = self.canvas().size()
			size = s.width(), s.height()
	
			im = self.image.resize(size)
			im.save("/tmp/test.png")
			del im
		
			pixmap = QPixmap()
			pixmap.load('/tmp/test.png')
			if QT_VERSION_STR[0] == '2':
				self.canvas().setBackgroundPixmap(pixmap)
			else:
				self.canvas().setPaletteBackgroundPixmap(pixmap)
		#else:
			#raise ?

	def zoom(self, x0, y0, x1, y1):
		x0, y0, x1, y1 = map(int, (x0, y0, x1, y1))
		if not self.rescale_on_zoom:
			if not hasattr(self, "image_unzoomed"):
				self.image_unzoomed = copy.copy(self.image)
			unz = self.image_unzoomed
			y_top = unz.size[1]
			flip = lambda y: y_top - y
			if y1 > y0:
				y0, y1 = y1, y0
			self.image = copy.copy(unz)
			self.image = self.image.transform(unz.size, Image.EXTENT,
											  (x0, flip(y0), x1, flip(y1)))
		else:
			if y1 < y0:
				y0, y1 = y1, y0
			#print x0, x1, y0, y1
			#print shape(self.array)
			arr = self.array[y0 : y1, x0 : x1]
			self.image = pilutil.toimage(MLab.flipud(arr),
										 pal = self.palette)
			if self.legend:
				self.legend.setImagePlot(self, arr)
		self.doPlotImage()

	def unzoom(self):
		self.image = self.image_unzoomed
		self.doPlotImage()

	def resizeEvent(self, e):
		QwtPlot.resizeEvent(self, e)
		self.doPlotImage()

	#plotMousePressed (const QMouseEvent &e)
	#plotMouseReleased (const QMouseEvent &e)


class QwtImagePlotLegend(QwtImagePlot):
	def setImagePlot(self, implot, arr = None):
		self.implot = implot
		implot.legend = self

		self.parent_array = arr or implot.array
		self.palette = implot.palette

		r = ravel(self.parent_array)
		r_min, r_max = min(r), max(r)

		dif = r_max - r_min
		if dif == 0:
			r_max = r_min + 1
		self.array = arange(r_min, r_max, dif / 256.)[:,NewAxis]
		
		self.setAxisScale(QwtPlot.yLeft, r_min, r_max)
		self.replot()
		
		# if no_scaling: #for subplots and stuff like that...
		#  im = pilutil.toimage(MLab.flipud(arr), pal = palette, cmin = 0., cmax = 1.)
		self.image = pilutil.toimage(MLab.flipud(self.array), pal = self.palette)
		self.doPlotImage()
	

class QwtImagePlotZoom(QwtImagePlot):
	def __init__(self, parent=None):
		QwtImagePlot.__init__(self, parent)
		
		if False:
			self.graph = QwtImagePlot("Check the stack order of the bars: "
									  "leftclick and drag to zoom, "
									  "rightclick to unzoom.", self)
			self.setCentralWidget(self.graph)
			self.graph.canvas().setMouseTracking(1)
		else:
			self.canvas().setMouseTracking(1)


		self.zoomStack = []
		self.connect(self,
					 SIGNAL('plotMousePressed(const QMouseEvent&)'),
					 self.onMousePressed)
		self.connect(self,
					 SIGNAL('plotMouseReleased(const QMouseEvent&)'),
					 self.onMouseReleased)

		if False:
			# The number of bars -- the widget gets slow for more than 1000 bars
			self.toolBar = QToolBar(self)
			self.toolBar.setStretchableWidget(QWidget(self.toolBar))

		if False:
			counterBox = QHBox(self.toolBar)
			counterBox.setSpacing(10)
			QLabel("Number of bars", counterBox)
			self.counter = QwtCounter(counterBox)
			self.counter.setRange(0, 10000, 1)
			self.counter.setValue(0)
			self.counter.setNumButtons(3)
			self.connect(self.counter, SIGNAL('valueChanged(double)'), self.plot)
	
	def onMousePressed(self, e):
		if Qt.LeftButton == e.button():
			# Python semantics: self.pos = e.pos() does not work; force a copy
			self.xpos = e.pos().x()
			self.ypos = e.pos().y()
			self.enableOutline(1)
			self.setOutlinePen(QPen(Qt.black))
			self.setOutlineStyle(Qwt.Rect)
			self.zooming = 1
			if self.zoomStack == []:
				self.zoomState = (
					self.axisScale(QwtPlot.xBottom).lBound(),
					self.axisScale(QwtPlot.xBottom).hBound(),
					self.axisScale(QwtPlot.yLeft).lBound(),
					self.axisScale(QwtPlot.yLeft).hBound(),
					)
		elif Qt.RightButton == e.button():
			self.zooming = 0

	def onMouseReleased(self, e):
		if Qt.LeftButton == e.button():
			xmin = min(self.xpos, e.pos().x())
			xmax = max(self.xpos, e.pos().x())
			ymin = min(self.ypos, e.pos().y())
			ymax = max(self.ypos, e.pos().y())
			self.setOutlineStyle(Qwt.Cross)
			xmin = int(self.invTransform(QwtPlot.xBottom, xmin))
			xmax = int(self.invTransform(QwtPlot.xBottom, xmax))
			ymin = int(self.invTransform(QwtPlot.yLeft, ymin))
			ymax = int(self.invTransform(QwtPlot.yLeft, ymax))
			if xmin == xmax or ymin == ymax:
				return
			self.zoomStack.append(self.zoomState)
			self.zoomState = (xmin, xmax, ymin, ymax)
			self.enableOutline(0)
		elif Qt.RightButton == e.button():
			if len(self.zoomStack):
				xmin, xmax, ymin, ymax = self.zoomStack.pop()
			else:
				return

		self.setAxisScale(QwtPlot.xBottom, xmin, xmax)
		self.setAxisScale(QwtPlot.yLeft, ymin, ymax)
		# print xmin, ymin, xmax, ymax

		self.zoom(xmin, ymin, xmax, ymax)
		self.replot()




class MyImagePlot(QWidget):
    #	def __init__(self, parent=None):
	#	QWidget.__init__(self, parent)

	#this fucks up the workspace-idea:
	def __init__(self, app, *args):
		apply(QWidget.__init__, (self,) + args)

		self.qvbox = QVBox(self)

		self.imageplot = QwtImagePlotZoom(self.qvbox)
		self.imageplot.setArray(testArray(1000))
		self.imageplot.resize(300, 300)

		self.resize(400, 400)

		#self.qvbox = QVBox(self.qvbox)
		#self.qvbox.setMaximumWidth(90)

		"""
		self.chkRescale = QCheckBox(self.qvbox)
		self.chkRescale.setText("&rescale\non\nzoom")

		self.cmbPalettes = QComboBox(self.qvbox)
		for key in palettes.keys():
			self.cmbPalettes.insertItem(key)

		self.legend = QwtImagePlotLegend(self.qvbox)
		self.legend.setImagePlot(self.imageplot)
		self.legend.show()

		self.chkRescale.show()
		#self.afterResize()

		self.connect(self.chkRescale, SIGNAL('clicked()'),
					 self.chkRescale_rescale_clicked)
		self.connect(self.cmbPalettes, SIGNAL('activated(const QString&)'),
					 self.cmbPalette_changed)
        #self.connect(self.cmbSource,SIGNAL('activated(const QString&)'),self.switchDataSource)
					 """
		
	def setArray(self, arr, palette = None, axis_x_max = None, axis_y_max = None):
		self.imageplot.setArray(arr)
		if palette:
			self.imageplot.setPalette(palette)

		s = shape(arr)
		axis_y_max = axis_y_max or s[0]
		axis_x_max = axis_x_max or s[1]

		#self.setAxisScale(QwtPlot.xBottom, 0, axis_x_max)
		#self.setAxisScale(QwtPlot.yLeft, 0, axis_y_max)
		#self.replot()

	def chkRescale_rescale_clicked(self):
		self.imageplot.rescale_on_zoom = self.chkRescale.isChecked()

	def cmbPalette_changed(self):
		self.imageplot.setPalette(palettes[str(self.cmbPalettes.currentText())])
		
	def afterResize(self):
		s = self.size()
		#self.imageplot.resize(s.width() - 70, s.height())
		#self.legend.setGeometry(s.width() - 70, 200, 70, 200)
		#self.chkRescale.setGeometry(s.width() - 70, s.height() - 40, 100, 45)
		self.qvbox.resize(s)
	
	def resizeEvent(self, e):
		self.afterResize()

	def setPalette(self, pal):
		self.legend.setPalette(pal)
		self.imageplot.setPalette(pal)


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
	try:
		__IPYTHON__
		ipython = True
	except:
		ipython = False

	if ipython:
		import iqt
	else:
		app = QApplication(sys.argv)

	w = QMainWindow()
	t = MyImagePlot(w)
	t.show()


	if False:
		w = QwtImagePlotZoom()
		w.resize(500, 500)
		w.setArray(testArray(1000),
				   palette = matlabtest)
		w.show()

	if False:
		l = QwtImagePlotLegend()
		l.setImagePlot(w)
		l.show()
	
	if not ipython:
		app.setMainWidget(w)
		app.exec_loop()
