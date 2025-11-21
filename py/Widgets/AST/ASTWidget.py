
from PySide6 import QtCore, QtWidgets, QtGui
import os

from typing import Any, Self

from py.Languages.AbstractSyntaxTree import ASTNode, ASTBranch
from py.Languages.Tokens import Token

class ASTRowWidgetContainer:
    pass

class ASTRowWidget(QtWidgets.QWidget):
    def __init__(
        self, 
        parent: ASTRowWidgetContainer, 
        lineNumber: int
    ):
        QtWidgets.QWidget.__init__(self, parent)
        self.lineNumber = lineNumber
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.widgets = []
        #self.setStyleSheet("margin: 0px; padding: 0px; background-color: blue")

    def addAstWidget(self, child: Self):
        self.layout.addWidget(child)
        self.widgets.append(child)
        
        width = 0
        height = 0
        for element in self.widgets:
            elementSize = element.sizeHint()
            width += elementSize.width()
            height = elementSize.height()
        
        size = QtCore.QSize(width, height)
        self.setMinimumSize(size)
        self.setMaximumSize(size)
             
class ASTWidget(QtWidgets.QWidget):
    def __init__(
        self, 
        node: ASTNode, 
        parent: QtWidgets.QWidget
    ):
        QtWidgets.QWidget.__init__(self, parent)
        parent.layout.addWidget(self)
        # self.setStyleSheet("margin: 0px; background-color: white")
        self.setProperty('type', node.type)
        self.setObjectName(node.type)
        # print(self.metaObject().className() + "#" + node.type)
        
    def addAstWidget(self, child: Self):
        raise NotImplementedError
             
class ASTBranchWidget(ASTWidget):
    def __init__(
        self,
        node: ASTNode,
        parent: QtWidgets.QWidget
    ):
        ASTWidget.__init__(self, node, parent)
        
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.setStyleSheet("margin: 0px")
        
    def addAstWidget(self, child: ASTWidget):
        self.layout.addWidget(child)
        
                
class ASTTokenWidget(ASTWidget):
    def __init__(
        self, 
        node: Token, 
        codeLine: str,
        parent: QtWidgets.QWidget
    ):
        ASTWidget.__init__(self, node, parent)
        self.setProperty('tokenName', node.tokenName)
        self.setProperty('code', node.code)
        self.characterWidgets = []
        
        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        width = 0
        height = 0
        for character in codeLine:
            characterWidget = ASTCharacterWidget(self, character)
            self.characterWidgets.append(characterWidget)
            self.layout.addWidget(characterWidget)
            characterSize = characterWidget.sizeHint()
            if characterSize.height() > height:
                height = characterSize.height()
            width += characterSize.width()
        
        size = QtCore.QSize(width, height)
        self.setMinimumSize(size)
        self.setMaximumSize(size)
        
class ASTCharacterWidget(QtWidgets.QWidget):
    def __init__(
        self,
        parent: ASTTokenWidget,
        character: str
    ):
        QtWidgets.QWidget.__init__(self)
        self.character = character
        
        self.label = ASTCharacterWidgetLabel(character, self)
        self.label.setScaledContents(False)
        self.label.setFont(QtGui.QFont('Monospace', 12))
        self.label.font().setStyleHint(QtGui.QFont.StyleHint.Monospace)
        self.setMinimumSize(self.label.sizeHint())
        self.setMaximumSize(self.label.sizeHint())
        
        self.label.setMouseTracking(True)
        self.setMouseTracking(True)
        
    def sizeHint(self):
        return self.label.sizeHint()
        
    #def moveEvent(self, event):
    #    print(event)
    #    QtWidgets.QWidget.moveEvent(self, event)
        
    def mouseMoveEvent(self, event):
        # print(event)
        if event.pos().x() > (self.width() / 2):
            self.label.showRightCursorPreview()
        else:
            self.label.showLeftCursorPreview()
        QtWidgets.QWidget.mouseMoveEvent(self, event)
        
    def enterEvent(self, event):
        # print(event)
        QtWidgets.QWidget.enterEvent(self, event)
        
    def leaveEvent(self, event):
        self.label.hideCursorPreview()
        # print(event)
        QtWidgets.QWidget.leaveEvent(self, event)
        
class ASTCharacterWidgetLabel(QtWidgets.QLabel):
    def __init__(self, character: str, parent: ASTCharacterWidget):
        QtWidgets.QLabel.__init__(self, character, parent)
        
    def showRightCursorPreview(self):
        self.setStyleSheet("border-right: 1px solid grey")
        
    def showLeftCursorPreview(self):
        self.setStyleSheet("border-left: 1px solid grey")
        
    def hideCursorPreview(self):
        self.setStyleSheet("")