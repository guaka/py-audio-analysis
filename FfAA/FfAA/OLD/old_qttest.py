#!/usr/bin/env ipython
#
# tree.py - a simple tree with QListView
#
import sys
from qt import *
from qwt import *


class QtFfAA(QListViewItem):
	def __init__(self, parent, object = None):
		# apply(QListViewItem.__init__, (self, parent))
		QListViewItem.__init__(self, parent, object.name)
		self.object = object
		self.setExpandable(True)
		self.c = []
		self.readable = True
		# print object.name
		
	def setup(self):
		if hasattr(self.object, "children") and self.object.children:
			self.setExpandable(True)
		else:
			self.setExpandable(False)
		QListViewItem.setup(self)

	def setOpen(self, o):
		if o and not self.childCount():
			for c in self.object.children:
				d = QtFfAA(self, c)
				self.c.append(d)
		QListViewItem.setOpen(self, o)



class MainWindow(QMainWindow):
	def __init__(self, structures, *args):
		apply(QMainWindow.__init__, (self,) + args)

		self.structures = structures

		self.tree = QListView(self)
		self.setCentralWidget(self.tree)

		self.tree.addColumn("item")
		self.tree.setRootIsDecorated(True)
		self.tree.setSorting(True, -1)

		self.items = []
		self.add_structures()

	def add_structures(self):
		for s in self.structures:
			node = QtFfAA(self.tree, s)
			self.items.append(node)
			# node.setOpen(True)
			pass
			# self.add_object(self.tree, s)
			
	def add_object(self, parent_node, object):
		node = QListViewItem(parent_node, object.name)
		self.items.append(node)
		for c in object.children:
			self.add_object(node, c)
		

	
if __name__ == "__main__":
	# testing for IPython may be subject to change

	import time

	print filter(lambda x: x.find("__IPYTHON") > -1, dir(__builtins__))
	
	ipython = ('__IPYTHON__active' in dir(__builtins__))
	print ipython
	
	if ipython:
		import iqt
	else:
		t = time.time()
		print t
		app = QApplication(sys.argv)
		print time.time() - t

	try:
		import Structures
		s = Structures.structures
	except ImportError: 
		s = []
		
	win = MainWindow(s)
	win.show()

	if not ipython:
		app.connect(app, SIGNAL("lastWindowClosed()"),
					app, SLOT("quit()"))
		app.exec_loop()
				

