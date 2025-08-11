
from PySide6 import QtCore, QtWidgets, QtGui
import os

from py.Hub import Hub, Log, on
from py.Api import TextField as TextFieldApi
from py.Languages.AbstractSyntaxTree import ASTRoot, ASTBranch, ASTNode
from py.Languages.Tokens import Token
from py.Widgets.AST.ASTWidget import ASTWidget, ASTRowWidget, ASTRowWidgetContainer
from py.Widgets.AST.ASTWidget import ASTBranchWidget, ASTTokenWidget
from py.Widgets.AST.ASTRootWidget import ASTRootWidget

class ASTTextField(QtWidgets.QWidget, TextFieldApi, ASTRowWidgetContainer):
    def __init__(
        self, 
        parent: QtWidgets.QWidget, 
        hub: Hub
    ):
        QtWidgets.QWidget.__init__(self, parent)
        
        self._document = QtGui.QTextDocument(self)
        self.hub = hub
        self.hub.setup(self)
        self.hub.register(self._document)
        
        self.setMinimumSize(QtCore.QSize(500, 500))
        
        self._document.contentsChanged.connect(self.onDocumentContentsChanged)
        
        self.rows = []
        
        label = QtWidgets.QLabel()
        
        self.layout = QtWidgets.QVBoxLayout(self)
        
    @on(ASTRoot)
    def onNewAST(self):
        self._processNewAst(self.hub.get(ASTRoot))
        
    def _processNewAst(self, root: ASTRoot):
        print("QWEQWEQWE")
        # ASTRootWidget(root)
        
        self.rows = []
        self.rows.append(ASTRowWidget(self, 0))
        self.layout.addWidget(self.rows[0])
        
        for node in root.children:
            self._nodeToWidget(node, root, self, self.rows[0])
    
        self.show()
        
#    def _nodesToWidget(
#        self, 
#        parent: ASTWidget, 
#        nodes, 
#        lastRow: ASTRowWidget
#    ):
#        for node in nodes:
#            self._nodeToWidget(node, parent, self, lastRow)
        
    def _nodeToWidget(
        self, 
        node: ASTNode,
        parentNode: ASTBranch,
        parentWidget: QtWidgets.QWidget,
        lastRow: ASTRowWidget
    ):
        widget = None
        if isinstance(node, Token):
            print(node)
            widget = ASTTokenWidget(node, parentWidget)
        elif isinstance(node, ASTBranch):
            widget = ASTBranchWidget(node, parentWidget)
            for child in node.children:
                self._nodeToWidget(child, node, widget, lastRow)
        else:
            raise Error("Unknown AST node class: " + type(node))
        lastRow.addAstWidget(widget)
        
    ### QTextDocument
    
    def onDocumentContentsChanged(self):
        text = self._document.toPlainText()
        # print(text)
        
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