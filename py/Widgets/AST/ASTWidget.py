
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
        # self.setLayout(self.layout)
        # self.layout.addWidget(QtWidgets.QLabel("dolor", self))
        self.setStyleSheet("border: 1px solid red; margin: 0px; padding: 1px; background-color: blue")

    def addAstWidget(self, child: Self):
        self.layout.addWidget(child)
             
class ASTWidget(QtWidgets.QWidget):
    def __init__(
        self, 
        node: ASTNode, 
        parent: QtWidgets.QWidget
    ):
        QtWidgets.QWidget.__init__(self, parent)
        parent.layout.addWidget(self)
        self.setStyleSheet("border: 1px solid black; margin: 0px; background-color: red")
        # self.show()
        
    def addAstWidget(self, child: Self):
        raise NotImplementedError
             
#class ASTRootWidget(ASTWidget):
#    def __init__(
#        self, 
#        astRoot: ASTRoot
#        parent: 
#    ):
#        ASTWidget.__init__(self, astRoot, 0)
   
class ASTBranchWidget(ASTWidget):
    def __init__(
        self,
        node: ASTBranch,
        parent: QtWidgets.QWidget
    ):
        ASTWidget.__init__(self, node, parent)
        
        self.layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(self.layout)
        
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
        
        # self.layout = QtWidgets.QHBoxLayout(self)
        # self.setLayout(self.layout)
        self.label = QtWidgets.QLabel(codeLine, self)
        self.label.setScaledContents(False)
        self.label.font().setStyleHint(QtGui.QFont.StyleHint.Monospace)
        #self.layout.addWidget(self.label)

        self.setMinimumSize(self.label.sizeHint())
        self.setMaximumSize(self.label.sizeHint())
        
        # print("ASD")
        # print(node.code)
        # print(self.label.sizeHint())
        