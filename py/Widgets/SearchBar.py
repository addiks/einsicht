
from PySide6 import QtCore, QtWidgets, QtGui
import os

class SearchBar(QtWidgets.QWidget):
    def __init__(self, editorWindow):
        super().__init__()
        self.hide()
        
        self.editorWindow = editorWindow
        
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
            
    def onTextChanged(self): 
        print("onTextChanged")
        print(self.lineEdit.text())
        
        pattern = self.lineEdit.text()
        
        document = self.editorWindow.textField.document()
        text = doc.toPlainText()
        offset = 0
        results = []
       
        position = text.find(pattern, offset)
        while position >= offset:
            results.append(SearchOccurence(position, pattern, pattern))
            position = text.find(pattern, offset)
            
        self.editorWindow.updateInlineSearchResults(results)
            
class SearchOccurence:
    def __init__(self, offset, pattern, text):
        self.offset = offset
        self.pattern = pattern
        self.text = text