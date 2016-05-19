#! /usr/bin/python
from PyQt4 import QtGui, QtCore
import numpy as np

import time
import socket
import sys
import os
from PyQt4 import Qt
sys.path.insert(1, os.path.join(sys.path[0], '..'))
import client


class RenderArea(QtGui.QWidget):

    def __init__(self, parent=None):
        super(RenderArea, self).__init__(parent)
        self.data = np.zeros((10,10))

        host = socket.gethostname() # Get local machine name
        port = 12345                # Reserve a port for your service.
        res, self.sock = client.estConnection(host, port)
        time.sleep(0.0005)
        if res == 0:
            raise Exception("ERROR> Connection could not be established")
        self.EOG = False
        buff = self.sock.recv(2048)
        client.saveSend(self.sock, "Y")
        self.data = client.fieldRequest(self.sock)

    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        for i in range(10):
            for j in range(10):
                if self.data[i, j] == 0:
                    color = QtCore.Qt.blue
                elif self.data[i, j] == 1:
                    color = QtCore.Qt.yellow
                elif self.data[i, j] == 2:
                    color = QtCore.Qt.green
                elif self.data[i, j] == 3:
                    color = QtCore.Qt.red
                painter.fillRect(QtCore.QRect(i*50, j*50, 50, 50), color)

    def mousePressEvent(self, QMouseEvent):
        x = QMouseEvent.pos().x()
        y = QMouseEvent.pos().y()

        print x,y
        i = x/50
        j = y/50
        if self.data[i, j] != 0:
            return
        client.bomb(self.sock, i, j)
        buff = self.sock.recv(2048)
        print buff
        if buff == "EOG":
            self.sock.close()
            self.data[i, j] = 3
            self.update()
            message = QtGui.QMessageBox(text="Spiel beendet")
            message.show()
            message.exec_()
            return
        client.saveSend(self.sock,"Y")
        self.data = client.fieldRequest(self.sock)
        self.update()

if __name__ == "__main__":
    a = Qt.QApplication(sys.argv)
    mainWindow = Qt.QMainWindow()
    mainWindow.setMinimumHeight(500)
    mainWindow.setMinimumWidth(500)
    ra = RenderArea()
    mainWindow.setCentralWidget(ra)
    mainWindow.show()

    a.exec_()
