#! /usr/bin/python
from PyQt4 import QtGui, QtCore
import numpy as np

import time
import socket
import sys
import os
from PyQt4 import Qt
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from gameClass import *


class RenderArea(QtGui.QWidget):

    def __init__(self, parent=None):
        super(RenderArea, self).__init__(parent)
        self.data = np.zeros((10,10))

        self.gInst = game()
        gameState = self.gInst.initRound()
        if (gameState != 1):
          raise "ERROR> first round could not be initiated"
        self.data = self.gInst.fieldRequest()
        self.round = 0

    def paintEvent(self, QPaintEvent):
        painter = QtGui.QPainter(self)
        for i in range(10):
            for j in range(10):
                if self.data[i, j] == 0:
                    color = QtCore.Qt.gray
                elif self.data[i, j] == 1:
                    color = QtCore.Qt.yellow
                elif self.data[i, j] == 2:
                    color = QtCore.Qt.blue
                elif self.data[i, j] == 3:
                    color = QtCore.Qt.red
                painter.fillRect(QtCore.QRect(i*50, j*50, 50, 50), color)
                painter.drawRect(QtCore.QRect(i*50, j*50, 50, 50))

    def mousePressEvent(self, QMouseEvent):
        x = QMouseEvent.pos().x()
        y = QMouseEvent.pos().y()

        print x,y
        i = x/50
        j = y/50
        if self.data[i, j] != 0:
            return
        self.gInst.bomb(i, j)
        self.round += 1
        gameState = self.gInst.initRound()

        if gameState == 0:
            self.gInst.closeConnection()
            self.data[i, j] = 3
            self.update()
            message = QtGui.QMessageBox(text="Game finished in {0:d} rounds".format(self.round))
            message.show()
            message.exec_()
            return
        else:
            self.data = self.gInst.fieldRequest()
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
