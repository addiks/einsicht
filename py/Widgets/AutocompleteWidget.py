
from PySide6 import QtCore, QtWidgets, QtGui

import os

from py.Hub import Hub

class AutocompleteWidget(QtWidgets.QListWidget):
    def __init__(self, editorWindow, hub: Hub, autocompletion):
        super().__init__(editorWindow.textField)
        self.hide()
        hub.setup(self)
        
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        # self.setFixedSize(100, 100)

        self.itemActivated.connect(self.onItemActivated)
        
        editorWindow.textField.textChanged.connect(self.hide)
        editorWindow.textField.selectionChanged.connect(self.hide)
        editorWindow.textField.cursorPositionChanged.connect(self.hide)
        
        self.editorWindow = editorWindow
        self.autocompletion = None
        self.changeAutocomplete(autocompletion)
        
    def onItemActivated(self, item):
        hub.registry(item.offer)
        self.hide()
        self.editorWindow.applyAutocompleOffer(item.offer)
        
    def changeAutocomplete(self, autocompletion):
        if self.autocompletion == autocompletion:
            return
        self.clear()
        
        self.autocompletion = autocompletion
        
        if self.autocompletion != None:
            hintedTexts = []
            number = 1
            for offer in self.autocompletion.provide():
                if offer.text in hintedTexts:
                    continue
                AutocompleteWidgetItem(self, offer, number)
                number += 1
                hintedTexts.append(offer.text)
        
        if self.count() > 0:
            cursorPosition = self.editorWindow.textField.cursorRect()
            self.move(cursorPosition.bottomLeft())
            self.show()
        else:
            self.hide()
            
    def setFocus(self):
        super().setFocus() 
        if self.count() > 0:
            self.item(0).setSelected(True)
            
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            self.onItemActivated(self.currentItem())
            #for item in self.selectedItems():
            #    self.onItemActivated(item)
            #    return True 
        elif event.key() == QtCore.Qt.Key_Up:
            index = self.currentRow() - 1
            if index < self.count():
                self.setCurrentRow(index)
        elif event.key() == QtCore.Qt.Key_Down:
            index = self.currentRow() + 1
            if index < self.count():
                self.setCurrentRow(index)
        else:
            super().keyPressEvent(event)
              
class AutocompleteWidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, parent, autocompleteOffer, number):
        super().__init__(str(number).rjust(3) + " " + autocompleteOffer.text, parent)
        self.setFont(QtGui.QFont("Mono"))
        self.offer = autocompleteOffer
        self.number = number
          
    def keyPressEvent(self, event):
        print([event.key()])
        super().keyPressEvent(event)
            