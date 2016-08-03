#!/usr/bin/python

import sys
import os
from qt import *

import xmms
from Numeric import transpose

from SoundInfo import SoundInfo
from QImagePlot import QImagePlotCached

class SoundInfoCache:
	def __init__(self, parent, filename, title = ""):
		self.parent = parent
		self.filename = filename
		self.title = title or filename

		self.fP = filename + "PCoC.png"
		self.fS = filename + "SimRel.png"
		self.fF = filename + "FFT.png"
		
		if not (os.path.exists(self.fP) or
				os.path.exists(self.fS) or
				os.path.exists(self.fF)):
			self.soundinfo = SoundInfo(filename)

			self.vPCoC = self.thingy(self.fP, transpose(self.soundinfo.PC_cepstr.arr))
			self.vSimrel = self.thingy(self.fS, self.soundinfo.simrel.arr)
			self.vFFT = self.thingy(self.fF, transpose(self.soundinfo.fft))
		else:
			self.vPCoC = self.thingy(self.fP)
			self.vSimrel = self.thingy(self.fS)
			self.vFFT = self.thingy(self.fF)
			

	def thingy(self, filename, arr = None):
		q = QImagePlotCached(self.parent, filename, arr)
		q.hide()
		return q
	
	def repaint(self, paint, h, w):
		self.vPCoC.resize(w, h)
		pic = QPixmap(self.vPCoC.filename)
		paint.drawPixmap(0, 0, pic)
		
		self.vSimrel.resize(w, h)
		pic = QPixmap(self.vSimrel.filename)
		paint.drawPixmap(0, h, pic)

		self.vFFT.resize(w, h)
		pic = QPixmap(self.vFFT.filename)
		paint.drawPixmap(0, h * 2, pic)


class SoundInfoWidget(QWidget):
	def __init__(self, parent=None, name=None):
		QWidget.__init__(self, parent, name)
		self.setMinimumSize(400, 400)

		self.item = None

		paint = QPainter(self)
		paint.setBrush(QColor(255, 0, 0))
		#paint.drawLine(0, 0, 500,0)

		self.time = QTime.currentTime()
		internalTimer = QTimer(self)
		self.connect(internalTimer, SIGNAL("timeout()"), self.timeout)
		internalTimer.start(100)
		
	def timeout(self):
		new_time = QTime.currentTime()
		if new_time.second() != self.time.second():
			self.update()

	def paintEvent(self, qe):
		if not self.isVisible() or not xmms.is_running():
			return
		self.time = QTime.currentTime()
		
		pts = QPointArray()
		paint = QPainter(self)

		xmms_pos = (1.0 * xmms.get_output_time() /
					xmms.get_playlist_time(xmms.get_playlist_pos()))
		# paint.setBrush(QColor(255, 255 * xmms_pos, 255 * xmms_pos))
		paint.setPen(QColor(255, 255, 255))

		h = self.height() / 3
		if hasattr(self, "soundinfocache"):
			self.soundinfocache.repaint(paint, h, self.width())
			paint.drawText(0, 500, self.soundinfocache.title)
		s = xmms_pos * self.width()
		paint.drawRect(max(0, s), 0, 1, self.height())
		paint.drawRect(0, h * (2 - xmms_pos), self.width(), 1)

	def setItem(self, item):
		self.item = item
		if not hasattr(item, "soundinfocache"):
			self.soundinfocache = SoundInfoCache(self, item.file, item.title)

	def mouseDoubleClickEvent(self, ev):
		if self.item:
			pos = self.item.dur * ev.pos().x() / self.width()
			print pos
			print self.item.file
			xmms.set_playlist_pos(self.item.playlist_pos)
			xmms.jump_to_time(pos)

		self.drawTime()

	def drawTime(self):
		pos = int(1.0 * xmms.get_output_time() / self.item.dur * self.width())
		print pos 



class CentralWidget(QSplitter):
	def __init__(self, *args):
		apply(QSplitter.__init__, (self,) + args)
		self.setupListView()

		self.infowidget = SoundInfoWidget(self)

	def setupListView(self):
		self.qvbox = QVBox(self)

		buttons = QHBox(self.qvbox)
		
		getxmms = QPushButton('Get &Playlist', buttons, 'getplaylist')
		getxmms.setFont(QFont('Times',18,QFont.Bold))
		self.connect(getxmms, SIGNAL('clicked()'), self.getxmmsinfo)

		calc = QPushButton('&Calculate', buttons, 'calc')
		calc.setFont(QFont('Times',18,QFont.Bold))
		self.connect(calc, SIGNAL('clicked()'), self.calculate)

		self.listView = QListView(self.qvbox)
		#self.listView.setMaximumWidth(400)
		self.listView.addColumn('listpos')
		self.listView.addColumn('title')
		self.listView.addColumn('duration')
		self.listView.setSorting(False)
		#self.connect(self.listView, SIGNAL('clicked(QListViewItem*)'), self.listView.selectedItem())
		self.listView.setAllColumnsShowFocus(True)

		self.getxmmsinfo()

	def getxmmsinfo(self):
		while self.listView.lastItem():
			self.listView.takeItem(self.listView.lastItem())
		
		self.xmms_playlist = []
		cur_pos = xmms.get_playlist_pos()
		for i in range(xmms.get_playlist_length()):
			item = QListViewItem(self.listView)
			item.playlist_pos = i
			item.title = xmms.get_playlist_title(i)
			item.dur = int(xmms.get_playlist_time(i))
			item.file = xmms.get_playlist_file(i)
			self.xmms_playlist.append(item)
			
			dur_s = str(item.dur / 60000) + ":" + ("0" + str((item.dur / 1000) % 60))[-2:]
			pp = str(i + 1)
			item.setText(0, " " * (5 - len(pp)) + pp)
			item.setText(1, item.title)
			item.setText(2, dur_s)

			if cur_pos == i:
				self.listView.setSelected(item, True)

	#def itemSelected(self, item):
	#	self.selectedItem = item
	#	self.infowidget.setItem(item)

	def calculate(self):
		item = self.listView.selectedItem()		
		if item:
			self.infowidget.setItem(item)
		else:
			print "no item selected"

class MainWindow(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self, None, 'example addressbook application')

		self.filename = QString.null
		self.view = CentralWidget(self)
		self.setCentralWidget(self.view)

		self.showMaximized()
		#self.resize(900, 700)

def main():
	app = QApplication(sys.argv)
	
	mw = MainWindow()
	mw.setCaption('XMMS analyzer')
	app.setMainWidget(mw)
	mw.show()

	app.connect(app, SIGNAL("lastWindowClosed()"),
				app, SLOT("quit()"))
	app.exec_loop()

	for root, dirs, files in os.walk("."):
		for f in files:
			if os.path.splitext(f)[1] == ".wav":
				if ".mp3.wav" in f:
					print "Deleting ", f
					os.remove(f)

if __name__ == "__main__":
	main()


