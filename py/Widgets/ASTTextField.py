
from PySide6 import QtCore, QtWidgets, QtGui
import os

from py.Hub import Hub, Log, on
from py.Api import TextField as TextFieldApi
from py.Languages.AbstractSyntaxTree import ASTRoot, ASTBranch, ASTNode
from py.Languages.Tokens import Token
from py.Widgets.AST.ASTWidget import ASTWidget, ASTRowWidget, ASTRowWidgetContainer
from py.Widgets.AST.ASTWidget import ASTBranchWidget, ASTTokenWidget
from py.Widgets.AST.ASTRootWidget import ASTRootWidget

class ASTTextField(QtWidgets.QScrollArea, TextFieldApi, ASTRowWidgetContainer):
    def __init__(
        self, 
        parent: QtWidgets.QWidget, 
        hub: Hub
    ):
        QtWidgets.QScrollArea.__init__(self, parent)
        
        self.parent = parent
        self._document = QtGui.QTextDocument(self)
        self.hub = hub
        self.hub.setup(self)
        self.hub.register(self._document)
        
        self.setMinimumSize(QtCore.QSize(100, 100))
        
        self._document.contentsChanged.connect(self.onDocumentContentsChanged)
        
        self.rows = []
        
        label = QtWidgets.QLabel()
        
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
    @on(ASTRoot)
    def onNewAST(self):
        self._processNewAst(self.hub.get(ASTRoot))
        
    def _processNewAst(self, root: ASTRoot):
        self.rows = []
        self.rows.append(ASTRowWidget(self, 0))
        self.layout.addWidget(self.rows[0])
        
        parentWidget = self.rows[0]
        
        i=0
        for node in root.children:
            parentWidget = self._nodeToWidget(node, root, parentWidget)
            i+=1
            if i > 200:
                break
        
        self._addSpacerToLayout(parentWidget.layout)
    
        self._addSpacerToLayout(self.layout)
    
        minimumWidth = 100    
        heightSum = 0
        for row in self.rows:
            rowSize = row.sizeHint()
            heightSum += rowSize.height()
            minimumWidth = max(100, min(1000, max(minimumWidth, rowSize.width())))
            print(rowSize)
            
        self.setMinimumSize(
            minimumWidth, 
            max(100, min(1000, heightSum))
        )
        
        self.parent.adjustSize()
        self.parent.updateGeometry()
        
    def _nodeToWidget(
        self, 
        node: ASTNode,
        parentNode: ASTBranch,
        parentWidget: QtWidgets.QWidget
    ):
        if isinstance(node, Token):
            print(node)
            codeLines = node.code.split("\n")
            print(codeLines)
            for index, codeLine in enumerate(codeLines):
                print(codeLine)
                if len(codeLine) > 0:
                    ASTTokenWidget(node, codeLine, parentWidget)
                if len(codeLines) > index + 1:
                    row = ASTRowWidget(self, node.row + index)
                    self.rows.append(row)
                    self.layout.addWidget(row)
                    self._addSpacerToLayout(parentWidget.layout)
                    parentWidget = row
        elif isinstance(node, ASTBranch) and False:
            widget = ASTBranchWidget(node, parentWidget)
            for child in node.children:
                parentWidget = self._nodeToWidget(child, node, widget)
        else:
            raise Error("Unknown AST node class: " + type(node))
        return parentWidget
        # lastRow.addAstWidget(widget)
        
    def _addSpacerToLayout(self, layout):
        layout.addSpacerItem(
            QtWidgets.QSpacerItem(
                0,
                0, 
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum
            )
        )
        
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