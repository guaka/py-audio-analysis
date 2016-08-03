#!/usr/bin/env ipython
#
import sys
import os

from qt import *
from qwt import *

import FfAA

import QtIcons	
import QImagePlot
import plot1d

import Numeric
import guaka_lib

from guaka_lib import isarray

class FfAAForm(QMainWindow):
	def __init__(self, parent = None, name = None, fl = 0):
		QMainWindow.__init__(self, parent, name, fl)
		self.setIcon(QPixmap(QtIcons.FfAA_icon))		
		#def __init__(self, *args):
        #apply(QMainWindow.__init__, (self,) + args)
		
		#self.setCaption("MDI Scribbler")
		self.workspace = QWorkspace(self, "workspace")
		self.winlist = []

		"""
		for i in range(10):
			win=Painting(self.workspace)
			win.resize(100,100)
			win.setCaption("Window " + str(i))
			self.winlist.append(win)
		"""
		self.setCentralWidget(self.workspace)

		self.setGeometry(0, 0, 500, 520)
		#self.statusBar()

		if not name:
			self.setName("FfAAForm")

		self.setCaption("QtFfAA - Framework for Audio Analysis")
		self.menu_stuff()

		self.browser = ObjectBrowser(self.workspace)
		self.tree = self.browser.tree
		self.winlist.append(self.browser)


	def menu_stuff(self):
		self.menubar = QMenuBar(self, "menubar")
		self.fileMenu = QPopupMenu(self)
		self.objectMenu = QPopupMenu(self)
		self.helpMenu = QPopupMenu(self)

		self.fileAddAction = MenuAction(self, "fileAddAction", "Add file(s)", "&Add",
										 menu = self.fileMenu,
										 image = QPixmap(QtIcons.image_open_data),
										 accelKey = "Ctrl+O")
		self.fileSaveAction = MenuAction(self, "fileSaveAction", "Save", "&Save",
										 menu = self.fileMenu,
										 accelKey = "Ctrl+S")
		self.fileExitAction = MenuAction(self, "fileExitAction", "Exit", "E&xit",
										 menu = self.fileMenu)
		self.objectCutAction = MenuAction(self, "objectCutAction", "Cut", "&Cut",
										  menu = self.objectMenu,
										  image = QPixmap(QtIcons.image_cut_data),
										  accelKey = "Ctrl+X")
		self.objectShowAction = MenuAction(self, "objectShowAction", "Show", "&Show",
										   menu = self.objectMenu,
										   accelKey = "Ctrl+W")
		self.objectReinitAction = MenuAction(self, "objectReinitAction", "Reinit", "&Reinit",
											 menu = self.objectMenu,
											 accelKey = "Ctrl+R")
		self.objectListenAction = MenuAction(self, "objectListenAction", "Listen", "&Listen",
											 menu = self.objectMenu,
											 accelKey = "Ctrl+L")
		self.objectSweepAction = MenuAction(self, "objectSweepAction", "Open in Sweep", "Open in Sw&eep",
											 menu = self.objectMenu)
		self.helpAboutAction = MenuAction(self, "helpAboutAction", "About", "&About",
										  menu = self.helpMenu)

		self.objectMenu.insertSeparator()

   		self.menubar.insertItem(QString(""), self.fileMenu, 0)
		self.menubar.insertItem(QString(""), self.objectMenu, 1)
		self.menubar.insertItem(QString(""), self.helpMenu, 2)

		self.menubar.findItem(0).setText(self.tr("&File"))
		self.menubar.findItem(1).setText(self.tr("&Object"))
		self.menubar.findItem(2).setText(self.tr("&Help"))

		# self.resize(QSize(200, 250).expandedTo(self.minimumSizeHint()))
		self.clearWState(Qt.WState_Polished)

		self.connect(self.fileAddAction, SIGNAL("activated()"), self.fileAdd)
		self.connect(self.fileSaveAction, SIGNAL("activated()"), self.fileSave)
		self.connect(self.fileExitAction, SIGNAL("activated()"), self.fileExit)
		self.connect(self.objectCutAction, SIGNAL("activated()"), self.objectCut)
		self.connect(self.objectShowAction, SIGNAL("activated()"), self.objectShow)
		self.connect(self.objectReinitAction, SIGNAL("activated()"), self.objectReinit)
		self.connect(self.objectListenAction, SIGNAL("activated()"), self.objectListen)
		self.connect(self.objectSweepAction, SIGNAL("activated()"), self.objectSweep)
		self.connect(self.helpAboutAction, SIGNAL("activated()"), self.helpAbout)

	def dropEvent(self, e):
		print e
		
	def fileSave(self):
		self.save_database()

	def fileAdd(self):
		if hasattr(self, "add_file_to_structures"):
			qf = QFileDialog()
			qf.setViewMode(qf.Detail)

			# problem with selecting multiple files using shift,
			# also sometimes very weird Gdk error on 2nd time...
			filenames = qf.getOpenFileNames("Music (*.ogg *.mp3 *.wav)", FfAA.Settings.default_music_dir,
											self, "FileDialog", "Choose file(s) to analyse")
			for f in map(str, filenames):
				self.add_file_to_structures(f)
				self.tree.add_structures()
		else:
			raise AttributeError

	def fileExit(self):
		# self.destroy()
		# TODO ask for saving
		if self.ipython:
			raise SystemExit, "IPythonExit"
		else:
			self.close()
	
	def objectCut(self):
		o = self.tree.currentItem().object
		if hasattr(o, "delete"):
			o.delete()
		self.tree.add_structures()
		
	def objectShow(self):
		o = self.tree.currentItem().object
		if isinstance(o, Structures.Processors.Processor):
			self.show_processor(o)
		elif isinstance(o, Structures.Relations.Similarity_Relation):
			self.show_similarity_relation(o)
		elif isarray(o):
			self.show_array(o)
		elif FfAA.is_FfAA_instance(o) and hasattr(o, "show"):
			o.show()

	def objectReinit(self):
		o = self.tree.currentItem().object
		if hasattr(o, "reinit"):
			o.reinit()

	def objectListen(self):
		o = self.tree.currentItem().object
		if hasattr(o, "source"):
			o.source.listen()
		else:
			print "Object has no source attribute!"

	def objectSweep(self):
		o = self.tree.currentItem().object
		if hasattr(o, "source"):
			o.source.open_with("sweep")
		else:
			print "Object has no source attribute!"


	def helpAbout(self):
		QMessageBox.about(self, 
						  "QtFfAA", 
						  'This is a Qt viewer for the FfAA Structure database\n' +
						  'Written in Python, with the help of many libraries\n\n' + 
						  'by Kasper.Souren@ircam.fr')

		
	def add_window(self, win, title = "plot", width = 450, height = 300):
		self.winlist.append(win)
		win.resize(width, height)
		win.setCaption(title)
		win.show()

	def show_processor(self, p):
		win = QImagePlot.MyImagePlot(self.workspace)
		win.imageplot.setArray(Numeric.transpose(p.feature_vectors),
							   palette = QImagePlot.palettes["matlabtest"],
							   axis_x_max = p.source.length,
							   object = p) #, axis_y_max = axis_y_max)
		self.add_window(win, title = p.source.name + " - " + p.name)


	def show_similarity_relation(self, p):
		print "def show_similarity_relation(self, p):"
		#win = QImagePlot.QwtImagePlotZoom(self.workspace)
		win = QImagePlot.MyImagePlot(self.workspace)
		print p.source.length
		win.setArray(p.R,
					 palette = QImagePlot.palettes["brownish"],
					 axis_x_max = p.source.length,
					 axis_y_max = p.source.length,
					 object = p)
		self.add_window(win, title = p.source.name + " - " + p.name,
						width = 350, height = 350)


	def show_array(self, p):
		if len(shape(p)) == 1:
			self.plot1d(p)
		else:
			win = QImagePlot.MyImagePlot(self.workspace)
			win.setArray(p,
						 palette = QImagePlot.palettes["brownish"])
			self.add_window(win, title = "array",
							width = 350, height = 350)
			

	def imageplot(self, arr, title = None, palette = None, axis_x_max = None, axis_y_max = None):
		title = title or "imageplot"
		#win = QImagePlot.QwtImagePlotZoom(self.workspace)
		win = QImagePlot.MyImagePlot(self.workspace)
		win.setArray(arr, palette = palette, axis_x_max = axis_x_max, axis_y_max = axis_y_max)
		self.add_window(win, title = title)

	def plot1d(self, arr, title = None):
		title = title or "1D plot"
		win = QwtPlot(self.workspace)
		crv = win.insertCurve("test")
		win.setCurvePen(crv, QPen(Qt.red))
		win.setCurveData(crv, Numeric.arange(len(arr)), arr)

		win.plotLayout().setMargin(0)
		win.plotLayout().setCanvasMargin(0)
		#win.plotLayout().setAlignCanvasToTicks(10)

		win.replot()
		self.add_window(win, title = title)

	def borderplot(self, data, title = "1D plot"):
		win = plot1d.CurveDemo()
		win.set_data(data)
		self.add_window(win, title = title)

	def showlist(self, l, title = "list"):
		win = QListBox(self.workspace)
		for i in l:
			win.insertItem(i)
		self.add_window(win, title = title)


class MenuAction(QAction):
	def __init__(self, parent, name, text, menutext,
				 menu = None,
				 image = None,
				 accelKey = None):

		QAction.__init__(self, parent, name)
		# self.helpAboutAction = QAction(self, name)
		self.setText(self.tr(text))
		self.setMenuText(self.tr(menutext))
		if accelKey:
			self.setAccel(self.tr(accelKey))
		else:
			self.setAccel(QString.null)
		self.addTo(menu)
		if image:
			self.setIconSet(QIconSet(image))
			


class ObjectNode(QListViewItem):
	def __init__(self, parent, object = None, name = ""):
		# apply(QListViewItem.__init__, (self, parent))
		QListViewItem.__init__(self, parent, name)
		self.object = object
		self.setExpandable(True)
		self.children = []
		self.readable = True
		# print object.name
		
	def setup(self):
		o = self.object
		if FfAA.is_FfAA_instance(o):
			self.setExpandable(True)
		else:
			self.setExpandable(False)
		QListViewItem.setup(self)

		"""
		elif hasattr(o, "__class__"):
			c = o.__class__
			print o.__class__, o
			if type(c) != type:
				self.setExpandable(True)
		"""


	def setOpen(self, obj):
		# print self, obj
		if obj:
			objChildren = self.object.children
			# this takes some time..
			# maybe object.len_children could be solution..
			if (not self.childCount() or
				not len(self.children) == len(objChildren)):
				self.deleteChildren()
				for (name, c_obj) in objChildren.items():
					d = ObjectNode(self, c_obj, name)
					self.children.append(d)
		QListViewItem.setOpen(self, obj)

	def deleteChildren(self):
		# TODO: first delete children!
		for c in self.children:
			self.takeItem(c)
		self.children = []

class ObjectTree(QListView):
	def __init__(self, parent):
		QListView.__init__(self, parent)

		self.addColumn("item")
		self.setRootIsDecorated(True)
		self.setSorting(0, True)
		self.items = []

	def set_structures(self, structures):
		self.structures = structures
		self.add_structures()

	def add_structures(self):
		self.delete_tree()
		if self.structures:
			for s in self.structures:
				node = ObjectNode(self, s, s.name)
				self.items.append(node)

	def delete_tree(self):
		for i in self.items:
			self.takeItem(i)
		self.items = []


class ObjectBrowser(QVBox):
	#def __init__(self, app, *args):
	#	apply(QWidget.__init__, (self,) + args)
	def __init__(self, parent):
		QVBox.__init__(self, parent)

		#self.vbox = QVBox(self)
		#self.setMinimumSize(300, 300)
		self.show()

		self.tree = ObjectTree(self)
		self.tree.show()

		self.textview = QTextView(self)
		self.textview.show()
		# self.show()
		self.textview.setMaximumHeight(45)

		self.resize(400, 400)
		self.setCaption("object browser")

		self.connect(self.tree, SIGNAL('selectionChanged()'), self.treeSelChanged)
		
	def treeSelChanged(self):
		node = self.tree.selectedItem()
		if node:
			#TODO: import repr
			obj = node.object
			if ((type(obj) == type(Numeric.array([])) and len(obj) > 100) or
				(type(obj) == str and len(obj) > 400)):
				s = "%s of size %i" % (type(obj).__name__, len(obj))
			else:
				s = repr(obj)
		else:
			s = ""
		self.textview.setText(s)

#def show(a, title = '', show_type = None):
def show(a, **args): #title = '', show_type = None):
	if type(a) == list:
		win.showlist(a, **args)
	elif isarray(a):
		l = len(Numeric.shape(a))
		if l == 1:
			win.plot1d(a, **args)
		elif l == 2:
			win.imageplot(a, **args)
		else:
			print Numeric.shape(a)


class QSongInfo(QWidget):
	def __init__(self, structure, *args):
		QWidget.__init__(self, *args)
		self.structure = structure

		self.qvbox = QVBox(self)
		self.simrel = QImagePlot.MyImagePlot(self.qvbox)
		self.simrel.setArray(Numeric.transpose(structure.Similarity_Relation.feature_vectors),
							 palette = QImagePlot.palettes["matlabtest"],
							 axis_x_max = structure.Similarity_Relation.source.length,
							 object = structure.Similarity_Relation) #, axis_y_max = axis_y_max)
		#self.add_window(win, title = p.source.name + " - " + p.name)



#=======================================

import my_show
my_show.show = show

try:
	import Structures # structures, init, save
	# structures = Structures.structures
except ImportError:
	print """
Can't import Structures
Can't do useful stuff!"""
	Structures = None




def main_win():
	win = FfAAForm()

	if Structures:
		win.tree.set_structures(Structures.structures)
		win.add_file_to_structures = Structures.init.add_files
		win.save_database = Structures.save

	win.show()
	return win


	
win = None


def main():
	global win, __IPYTHON__
	
	try:
		__IPYTHON__
		ipython = True
		print "from IPython"
	except:
		ipython = False
		print "not from IPython"

	if Structures and not Structures.structures is None:
		if ipython:
			import iqt
			win = main_win()
			win.ipython = ipython
			# from Interactive import *
		else:
			app = QApplication(sys.argv)
			win = main_win()
			win.ipython = ipython
			app.connect(app, SIGNAL("lastWindowClosed()"),
						app, SLOT("quit()"))
			app.exec_loop()

	
	structures_argv = []
	maximum = None
	print sys.argv[1]
	if sys.argv[1].find("ViewOne") >= 0:
		maximum = 1
		
	for f in sys.argv:
		for s in init.add_files(f, maximum = maximum):
			structures_argv.append(s)

	for s in structures_argv:
		Relations.Similar_Parts(s)
		Relations.Borders(s)
		s.Similarity_Relation.show()
		pass

if __name__ == "__main__":
	main()
		
		
