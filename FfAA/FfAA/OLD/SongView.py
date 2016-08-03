#!/usr/bin/env ipython

# The Python version of qwt-*/examples/simple_plot/simple.cpp

import sys
from qt import *
from qwt import *
from Numeric import *

from QImagePlot import QImagePlot

import FfAA
import Structures


class Thingy(QMainWindow):
	gridlayout = QGridLayout()

	gridlayout.add(QImagePlot())




def make():
    demo = QImagePlot()
    demo.resize(500, 300)
    demo.show()
    return demo

def main_win():
	win = QMainWindow()

	if False and Structures:
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


if __name__ == "__main__":
	main()
		



