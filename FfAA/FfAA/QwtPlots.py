#!/usr/bin/env python

# The Python version of qwt-*/examples/simple_plot/simple.cpp

import sys
from qt import *
from qwt import *
from Numeric import *


class SimplePlot(QwtPlot):
	def __init__(self, *args):
		apply(QwtPlot.__init__, (self,) + args)

		# make a QwtPlot widget
		#self.setTitle('A Simple PyQwt Plot Demonstration')
		#self.setAutoLegend(1)
		#self.setLegendPos(Qwt.Right)

		# set axis titles
		#self.setAxisTitle(QwtPlot.xBottom, 'x -->')
		#self.setAxisTitle(QwtPlot.yLeft, 'y -->')

		# insert a few curves
		cSin = self.insertCurve('y = sin(x)')
		cCos = self.insertCurve('y = cos(x)')

		# set curve styles
		self.setCurvePen(cSin, QPen(Qt.red))
		self.setCurvePen(cCos, QPen(Qt.blue))

		# calculate 3 NumPy arrays
		x = arrayrange(0.0, 50.0, 0.1)
		y = sin(x) + 2
		z = cos(x)

		# copy the data
		self.setCurveData(cSin, x, y)
		self.setCurveData(cCos, x, z)

		# insert a horizontal marker at y = 0
		#mY = self.insertLineMarker('y = 0', QwtPlot.yLeft)
		#self.setMarkerYPos(mY, 0.0)

		# insert a vertical marker at x = 2 pi
		#mX = self.insertLineMarker('x = 2 pi', QwtPlot.xBottom)
		#self.setMarkerXPos(mX, 2*pi)

		# replot
		self.replot()
	
	def add_curve(self, y, pen = QPen(Qt.red)):
		crv = self.insertCurve("test")
		self.setCurvePen(crv, pen)
		self.setCurveData(crv, arange(len(y)), y)
		self.replot()
		

def simple_plot_window(parent, arr):
	win = QwtPlot(parent)
	crv = win.insertCurve("test")
	win.setCurvePen(crv, QPen(Qt.red))
	win.setCurveData(crv, arange(len(arr)), arr)
	win.replot()
	return win
	

def make():
	demo = SimplePlot()
	demo.resize(500, 300)
	demo.show()
	return demo



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

	w = make()
	
	if not ipython:
		app.setMainWidget(w)
		app.exec_loop()




