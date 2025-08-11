
from PySide6 import QtCore, QtWidgets, QtGui
import os

from py.Languages.AbstractSyntaxTree import ASTRoot
from py.Widgets.AST.ASTWidget import ASTWidget

class ASTRootWidget(ASTWidget):
    def __init__(self, astRoot: ASTRoot):
        ASTWidget.__init__(self, astRoot, 0)
