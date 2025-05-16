
from PySide6 import QtCore, QtWidgets, QtGui

import os

class AutocompleteWidget(QtWidgets.QWidget):
    def __init__(self, parent, autocompletion):
        super().__init__(parent)
        self.autocompletion = autocompletion
        
        for offer in autocompletion.provide():
            print(offer)
        
