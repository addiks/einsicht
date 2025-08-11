
from PySide6 import QtCore, QtWidgets, QtGui
import os

from py.Hub import Hub, Log, on
from py.Api import TextField as TextFieldApi

# https://www.pythonguis.com/tutorials/qpropertyanimation/

class ASTTextField(QtWidgets.QWidget, TextFieldApi):
    def __init__(self, parent: QtWidgets.QWidget, hub: Hub):
        QtWidgets.QWidget.__init__(self, parent)
        
        self._document = QtGui.QTextDocument(self)
        self.hub = hub
        self.hub.setup(self)
        self.hub.register(self._document)
        
        self.setMinimumSize(QtCore.QSize(500, 500))
        
        self._document.contentsChanged.connect(self.onDocumentContentsChanged)
        
    ### QTextDocument
    
    def onDocumentContentsChanged(self):
        text = self._document.toPlainText()
        print(text)
        
    ### TextFieldApi
        
    def document(self):
        return self._document

    def insertTextAt(self, position, text):
        raise NotImplementedError
        
    def removeTextAt(self, position, length):
        raise NotImplementedError
        
    def indentIn(self):
        raise NotImplementedError
    
    def indentOut(self):
        raise NotImplementedError
    
    def deleteCurrentLines(self):
        raise NotImplementedError
    
    def scrollToLine(self, line):
        raise NotImplementedError
    
    def contentWidth(self):
        raise NotImplementedError
    
    def contentHeight(self):
        raise NotImplementedError
        
    def onStoppedTyping(self) -> None:
        self.hub.notify(TextFieldApi.onStoppedTyping)
      
    ### QWidget
    
    def ASDminimumSize(self):
        return QtCore.QSize(500, 500)  