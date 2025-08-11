
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
        self.layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.layout)
        self.setStyleSheet("border: 1px solid red; margin: 1px; padding: 1px; background-color: blue")

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
        self.setStyleSheet("border: 1px solid black; margin: 1px; background-color: red")
        self.show()
        
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
        parent: QtWidgets.QWidget
    ):
        ASTWidget.__init__(self, node, parent)
        
        self.layout = QtWidgets.QHBoxLayout(self)
        self.setLayout(self.layout)
        self.label = QtWidgets.QLabel(node.code, self)
        self.layout.addWidget(self.label)
