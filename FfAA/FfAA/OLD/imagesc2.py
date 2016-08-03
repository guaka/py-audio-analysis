#!/usr/bin/env python

import sys

from qt import *
from qwt import *
from Numeric import *

# from scipy.pilutil
def bytescale(data, cmin=None, cmax=None, high=255, low=0):
    if data.typecode == UInt8:
        return data
    high = high - low
    if cmin is None:
        cmin = min(ravel(data))
    if cmax is None:
        cmax = max(ravel(data))
    scale = high *1.0 / (cmax-cmin)
    bytedata = ((data*1.0-cmin)*scale + 0.4999).astype(UInt8)
    return bytedata + asarray(low).astype(UInt8)

def linearX(nx, ny):
    return repeat(arange(nx, typecode = Float32)[:, NewAxis], ny, -1)

def linearY(nx, ny):
    return repeat(arange(ny, typecode = Float32)[NewAxis, :], nx, 0)

class ImageFrame(QFrame):
    def __init__(self, *args):
        QFrame.__init__(self, *args)
        self.image = toQImage(bytescale(linearX(512, 256)))
        for i in range(0, 256):
            self.image.setColor(i, qRgb(i, 0, 255-i))
        self.setFixedSize(self.image.width(), self.image.height())
        self.setCursor(Qt.crossCursor)
        self.outlining = 0
        self.x0, self.y0, self.x1, self.y1 = 0, 0, 0, 0

    def drawContents(self, painter):
        painter.drawImage(0, 0, self.image)

    def drawOutline(self, painter):
        painter.setPen(Qt.white)
        painter.setRasterOp(Qt.XorROP)
        painter.setClipRect(self.contentsRect())
        painter.setClipping(1)
        painter.drawRect(self.x0, self.y0,
                         self.x1-self.x0+1, self.y1-self.y0+1)

    def mousePressEvent(self, event):
        painter = QPainter(self)

        if self.outlining:
            self.drawOutline(painter)

        self.x0 = self.x1 = event.pos().x()
        self.y0 = self.y1 = event.pos().y()

        self.outlining = 1
        self.drawOutline(painter)

        m = QMouseEvent(QEvent.MouseButtonPress,
                        QPoint(event.pos().x() - self.rect().topLeft().x(),
                               event.pos().y() - self.rect().topLeft().y()),
                        event.button(),
                        event.state())
        self.emit(PYSIGNAL('mousePressed'), (m,))
        
    def mouseReleaseEvent(self, event):
        if self.outlining:
            painter = QPainter(self)
            self.drawOutline(painter)

        self.outlining = 0
        
        m = QMouseEvent(QEvent.MouseButtonPress,
                        QPoint(event.pos().x() - self.rect().topLeft().x(),
                               event.pos().y() - self.rect().topLeft().y()),
                        event.button(),
                        event.state())
        self.emit(PYSIGNAL('mouseReleased'), (m,))

    def mouseMoveEvent(self, event):
        if self.outlining:
            painter = QPainter(self)
            self.drawOutline(painter)
            self.x1 = event.pos().x()
            self.y1 = event.pos().y()
            self.drawOutline(painter)
            
        m = QMouseEvent(QEvent.MouseMove,
                        QPoint(event.pos().x() - self.rect().topLeft().x(),
                               event.pos().y() - self.rect().topLeft().y()),
                        event.button(),
                        event.state())
        self.emit(PYSIGNAL('mouseMoved'), (m,))
    

class ImagePlot(QFrame):
    def __init__(self, *args):
        QFrame.__init__(self, *args)
        self.image = ImageFrame(self)
        self.image.setGeometry(64, 64, self.image.width(), self.image.height())
        self.resize(self.image.width()+2*64, self.image.height()+2*64)
        # -1 to trashes on image, but gives nicer scales
        self.x0Scale = QwtScaleDraw()
        self.x0Scale.setGeometry(64, 64+self.image.height()-1,
                                 self.image.width(),
                                 QwtScaleDraw.Bottom)
        self.x1Scale = QwtScaleDraw()
        self.x1Scale.setGeometry(64, 64,
                                 self.image.width(),
                                 QwtScaleDraw.Top)
        self.y0Scale = QwtScaleDraw()
        self.y0Scale.setGeometry(64, 64,
                                 self.image.height(),
                                 QwtScaleDraw.Left)
        self.y1Scale = QwtScaleDraw()
        self.y1Scale.setGeometry(64+self.image.width()-1, 64,
                                 self.image.height(),
                                 QwtScaleDraw.Right)
        print self.contentsRect().width()
        print self.contentsRect().height()

    def drawContents(self, painter):
        #painter.drawImage(64, 64, self.image)
        self.x0Scale.draw(painter)
        self.x1Scale.draw(painter)
        self.y0Scale.draw(painter)
        self.y1Scale.draw(painter)

def main(args):
    app = QApplication(args)
    demo = make()
    app.setMainWidget(demo)
    app.exec_loop()

def make():
    demo = ImagePlot()
    #demo = Frame()
    demo.show()
    return demo

if __name__ == '__main__':
    main(sys.argv)

