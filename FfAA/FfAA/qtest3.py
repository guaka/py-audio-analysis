#!/usr/bin/env python

# Form implementation generated from reading ui file 'frmconnect.ui'
#
# Created: Sat Oct 27 15:36:20 2001
#      by: The PyQt User Interface Compiler (pyuic)
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *


class frmConnect(QDialog):
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        QDialog.__init__(self,parent,name,modal,fl)

        if name == None:
            self.setName("frmConnect")

        self.resize(547,200)
        self.setCaption(self.trUtf8("Connecting"))
        self.setSizeGripEnabled(1)

        frmConnectLayout = QGridLayout(self,1,1,11,6,"frmConnectLayout")

        Layout5 = QVBoxLayout(None,0,6,"Layout5")

        self.buttonOk = QPushButton(self,"buttonOk")
        self.buttonOk.setText(self.trUtf8("&OK"))
        self.buttonOk.setAutoDefault(1)
        self.buttonOk.setDefault(1)
        Layout5.addWidget(self.buttonOk)

        self.buttonCancel = QPushButton(self,"buttonCancel")
        self.buttonCancel.setText(self.trUtf8("&Cancel"))
        self.buttonCancel.setAutoDefault(1)
        Layout5.addWidget(self.buttonCancel)

        self.buttonHelp = QPushButton(self,"buttonHelp")
        self.buttonHelp.setText(self.trUtf8("&Help"))
        self.buttonHelp.setAutoDefault(1)
        Layout5.addWidget(self.buttonHelp)
        spacer = QSpacerItem(20,20,QSizePolicy.Minimum,QSizePolicy.Expanding)
        Layout5.addItem(spacer)

        frmConnectLayout.addLayout(Layout5,0,1)

        self.grpConnection = QGroupBox(self,"grpConnection")
        self.grpConnection.setSizePolicy(QSizePolicy(5,7,0,0,self.grpConnection.sizePolicy().hasHeightForWidth()))
        self.grpConnection.setTitle(self.trUtf8(""))
        self.grpConnection.setColumnLayout(0,Qt.Vertical)
        self.grpConnection.layout().setSpacing(6)
        self.grpConnection.layout().setMargin(11)
        grpConnectionLayout = QGridLayout(self.grpConnection.layout())
        grpConnectionLayout.setAlignment(Qt.AlignTop)

        self.lblName = QLabel(self.grpConnection,"lblName")
        self.lblName.setText(self.trUtf8("&Name"))

        grpConnectionLayout.addWidget(self.lblName,0,0)

        self.lblHost = QLabel(self.grpConnection,"lblHost")
        self.lblHost.setText(self.trUtf8("&Host"))

        grpConnectionLayout.addWidget(self.lblHost,2,0)

        self.lblPasswd = QLabel(self.grpConnection,"lblPasswd")
        self.lblPasswd.setText(self.trUtf8("&Password"))

        grpConnectionLayout.addWidget(self.lblPasswd,1,0)

        self.txtPasswd = QLineEdit(self.grpConnection,"txtPasswd")
        self.txtPasswd.setMaxLength(8)
        self.txtPasswd.setEchoMode(QLineEdit.Password)

        grpConnectionLayout.addWidget(self.txtPasswd,1,1)

        self.cmbHostnames = QComboBox(0,self.grpConnection,"cmbHostnames")

        grpConnectionLayout.addWidget(self.cmbHostnames,2,1)

        self.txtName = QLineEdit(self.grpConnection,"txtName")
        self.txtName.setMaxLength(8)

        grpConnectionLayout.addWidget(self.txtName,0,1)

        frmConnectLayout.addWidget(self.grpConnection,0,0)

        self.connect(self.buttonOk,SIGNAL("clicked()"),self,SLOT("accept()"))
        self.connect(self.buttonCancel,SIGNAL("clicked()"),self,SLOT("reject()"))

        self.setTabOrder(self.txtName,self.txtPasswd)
        self.setTabOrder(self.txtPasswd,self.cmbHostnames)
        self.setTabOrder(self.cmbHostnames,self.buttonOk)
        self.setTabOrder(self.buttonOk,self.buttonCancel)
        self.setTabOrder(self.buttonCancel,self.buttonHelp)

        self.lblName.setBuddy(self.txtName)
        self.lblHost.setBuddy(self.cmbHostnames)
        self.lblPasswd.setBuddy(self.txtName)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = frmConnect()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
