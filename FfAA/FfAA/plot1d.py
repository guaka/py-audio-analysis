#!/usr/bin/env python

# The Python version of qwt-*/examples/curvedemo1/curvdemo1.cpp

# This examples demonstrate the use of keyword arguments in constructors, like:
#
# instance = ClassName(keyword1 = value1, keyword2 = value2, ..).
#
# Any method name can be used as a keyword. The value is a Python object,
# whose type depend on the method name (the object can be a tuple, if the
# method takes more than one argument).
#
# The keyword arguments feature is enabled by
# post-processing sip-generated *.py files.
#
# Warning: this feature is a HACK, only working in constructors!
# Qt's Designer and pyuic don't know about keyword arguments.
# If you code by hand, keyword arguments allow for shorter code.

import sys
from qt import *
from qwt import *
from Numeric import *

SIZE=30

arr = array([[  2.83000000e+02,	5.13384148e+00,	  6.66363479e+00],
			  [  7.86000000e+02,	4.86603777e+00,	  7.00851564e+00],
			  [  1.54900000e+03,	3.08731112e+00,	  7.07944309e+00],
			  [  1.79600000e+03,	1.47379809e+00,	  6.10988266e+00],
			  [  2.21200000e+03,	3.06825580e+00,	  7.01666254e+00],
			  [  2.74300000e+03,	1.79725014e+00,	  6.66369728e+00],
			  [  3.00100000e+03,	1.96671147e+00,	  7.15513952e+00],
			  [  4.64700000e+03,	8.65047790e+00,	  8.02380537e+00],
			  [  5.64700000e+03,	1.49665422e+00,	  7.66239731e+00],
			  [  5.95100000e+03,	1.10961250e+00,	  8.06388510e+00],
			  [  6.38400000e+03,	1.16423976e+00,	  6.64188059e+00],
			  [  6.98500000e+03,	1.05846605e+00,	  7.65935806e+00],
			  [  7.44700000e+03,	2.06469979e+00,	  6.38000152e+00],
			  [  8.04600000e+03,	1.01822208e+00,	  7.03134374e+00],
			  [  8.73700000e+03,	7.05998984e+00,	  5.54206768e+00],
			  [  1.03480000e+04,	5.11467472e+00,	  7.37386005e+00],
			  [  1.08480000e+04,	7.81279394e+00,	  4.84306622e+00],
			  [  1.26010000e+04,	1.50713002e+00,	  4.81830076e+00],
			  [  1.31470000e+04,	1.24584551e+00,	  4.87410294e+00],
			  [  1.36470000e+04,	3.34486373e+00,	  5.60992192e+00],
			  [  1.53010000e+04,	2.70679519e+00,	  5.63798087e+00],
			  [  1.67460000e+04,	1.36347149e+00,	  5.46208464e+00],
			  [  1.73450000e+04,	1.53947255e+00,	  4.84815497e+00],
			  [  1.77000000e+04,	1.43589866e+00,	  4.59227981e+00],
			  [  1.84150000e+04,	1.59304776e+00,	  4.84792800e+00],
			  [  1.95470000e+04,	2.08872286e+00,	  4.87979775e+00]])


class CurveDemo(QFrame):
	def __init__(self, *args):
		apply(QFrame.__init__, (self,) + args)

		#self.setFrameStyle(QFrame.Box | QFrame.Raised)
		#self.setLineWidth(2)
		#self.setMidLineWidth(3)
		# make curves with different styles
		# curve 1
		self.curve = QwtCurve(
			setPen = QPen(Qt.red), setStyle = QwtCurve.Sticks,
			setSymbol = QwtSymbol(QwtSymbol.Ellipse, QBrush(Qt.yellow),
								  QPen(Qt.blue), QSize(5, 5)))


	def set_data(self, data):
		# attach data, using Numeric
		self.x = arrayrange(0, 10.0, 10.0/SIZE)
		self.y = sin(self.x)*cos(2*self.x)

		self.x = data[:, 0]
		self.y = data[:, 1]

		self.curve.setData(self.x, self.y)
		self.xMap = QwtDiMap()
		self.xMap.setDblRange(self.x[0] - 1.5, self.x[-1] + 1.5, 0.0)
		self.yMap = QwtDiMap()
		self.yMap.setDblRange(max(self.y) + .1, .0, .0)

	def drawContents(self, painter):
		# draw curves
		r = self.contentsRect()
		dy = r.height() #/len(self.curve)
		r.setHeight(dy)
		if True: #for curve in self.curves:
			self.xMap.setIntRange(r.left(), r.right())
			self.yMap.setIntRange(r.top(), r.bottom())
			self.curve.draw(painter, self.xMap, self.yMap)
			r.moveBy(0, dy)
		# draw titles
		r = self.contentsRect()
		r.setHeight(dy)
		painter.setFont(QFont('Helvetica', 8))
		painter.setPen(Qt.black)


def make():
	demo = CurveDemo()
	demo.set_data(arr)
	demo.resize(300, 600)
	demo.show()
	return demo

def main(args):
	app = QApplication(args)
	demo = make()
	app.setMainWidget(demo)
	app.exec_loop()	   

# Admire!		  
if __name__ == '__main__':
	main(sys.argv)
