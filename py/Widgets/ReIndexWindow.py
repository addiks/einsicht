
from PySide6 import QtCore, QtWidgets, QtGui
import os

class ReIndexWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ReIndexWindow, self).__init__()

        self.centralWidget = QtWidgets.QWidget()
        self.centralWidget.layout = QtWidgets.QVBoxLayout(self.centralWidget)