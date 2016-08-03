#!/usr/bin/env python

import sys
from qt import *
from qwt import *

# import Structures


class MainWindow(QMainWindow):
	def __init__(self, structures, *args):
		apply(QMainWindow.__init__, (self,) + args)

		self.structures = structures

		self.tree = QListView(self)
		self.setCentralWidget(self.tree)
		self.tree.addColumn("item")
		self.tree.setRootIsDecorated(1)
		self.tree.setSorting(1, -1)

		self.items = []
		self.add_structures()

	def add_structures(self):
		for s in self.structures:
			self.add_object(self.tree, s)

	def add_object(self, parent_node, object):
		node = QListViewItem(parent_node, object.name)
		self.items.append(node)
		for c in object.children:
			pass #self.add_object(node, c)


class TreeView(QListView):
	def __init__(self, *args):
		QListView.__init__(self, *args)


class Compass(QwtCompass):
	def __init__(self, *args):
		QwtCompass.__init__(self, *args)
		self.setLineWidth(6)		
		self.setFrameShadow(QFrame.Raised)
		self.setRose(QwtCompassRose1(8, 2))
		self.scaleDraw().setTickLength(0, 0, 3)
		self.setNeedle(QwtCompassMagnetNeedle(Qt.blue, Qt.red))
		self.setAzimuth(220.0)

	# __init__()

# class Compass


def compass():
	c = Compass()
	c.show()
	return c


def test_python():
	result = compass()
	print "Testing 'raw_input()' to make 10 other compasses."
	raw_input('Happy? ')
	result = []
	for i in range(3):
		result.append(compass())
	print "Testing 'a = input(..)'"
	a = input("Type a Python statement, e.g 1+1: ")
	print "a =", a
	print "Now, you can try something like: a = test_python()"
	return result


def test_ipython():
	result = []
	for i in range(10):
		result.append(compass())
	print "Initially, input() and raw_input() are flaky,"
	print "but now you can try something like: a = test_python()"
	return result


def test():
	#mw = MainWindow(Structures.structures)
	t = TreeView()
	return t
	


# Admire!
if __name__ == '__main__':
	# testing for IPython may be subject to change
	if '__IPYTHON__active' in dir(__builtins__):
		import iqt
		# keep references to the widgets
		references = test()
	else:
		try:
			# check if ICompass.py is interpreted by something like PyCute
			qApp.argc()
		except RuntimeError:
			# fallback for a Command Line Interpreter
			import iqt
		# keep references to the widgets
		references = test()

# Local Variables: ***
# mode: python ***
# End: ***
