
from PySide6 import QtCore, QtWidgets, QtGui
import os

from py.Hub import Hub, Log

class SearchBar(QtWidgets.QWidget):
    def __init__(self, hub: Hub):
        super().__init__()
        hub.setup(self)
        self.hide()
        
        self.hub = hub
        self._results = []
        
        hbox = QtWidgets.QHBoxLayout(self)
        self.layout = hbox
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
         
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.textChanged.connect(self.onTextChanged)
        self.setFont(QtGui.QFont("Mono"))
        hbox.addWidget(self.lineEdit, 0) 

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.lineEdit.setFocus() 
            
    def searchOccurences(self):
        return self._results
            
    def onTextChanged(self): 
        pattern = self.lineEdit.text()
        
        document = self.hub.get(QtGui.QTextDocument)
        text = document.toPlainText()
        offset = 0
        line = 1
       
        results = []
        position = text.find(pattern, offset)
        while position >= offset:
            line += text[offset:position].count("\n")
            column = position - text.rfind("\n", 0, position) - 1
            if column == -1:
                column = 0
            results.append(InFileSearchOccurence(position, line, column, pattern, pattern))
            offset = position
            position = text.find(pattern, offset + 1)
            
        InFileSearchResult(results, self.hub)
             
class InFileSearchResult:
    def __init__(self, occurences, hub: Hub):
        self.hub = hub
        self.occurences = occurences
        self.currentIndex = 0
        self.hub.setup(self)
        if not self.empty():
            self.hub.register(self.current())
        
    def empty(self):
        return len(self.occurences) <= 0
        
    def current(self):
        return self.occurences[self.currentIndex]
        
    def activateNext(self):
        if self.currentIndex < len(self.occurences):
            self.current().deactivate()
            self.currentIndex += 1
            self.current().activate()
            self.hub.register(self.current())
        
    def activatePrevious(self):
        if self.currentIndex > 0:
            self.current().deactivate()
            self.currentIndex -= 1
            self.current().activate()
            self.hub.register(self.current())
             
class InFileSearchOccurence:
    def __init__(
        self, 
        offset: int, 
        line: int, 
        column: int, 
        pattern: str, 
        text: str
    ):
        self.offset = offset
        self.line = line
        self.column = column
        self.pattern = pattern
        self.text = text
        
    def activate(self):
        self.isActive = True
        
    def deactivate(self):
        self.isActive = False