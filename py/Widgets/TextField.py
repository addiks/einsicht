
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QTimer

from py.Autocomplete.AutocompleteItemModel import AutocompleteItemModel

class TextField(QtWidgets.QPlainTextEdit):
    
    def __init__(self, parent):
        QtWidgets.QPlainTextEdit.__init__(self, parent)
        
        self.parent = parent
        self._selectionChangeCounter = 0
        
        self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        
        self.document().setDefaultFont(QtGui.QFont("Mono"))
        
        self._completerItemModel = AutocompleteItemModel()
        self._completer = QtWidgets.QCompleter(self._completerItemModel)
        # self.setCompleter(self._completer)
        
        self._completer.setWidget(self)
        
        # self._completer.activated.connect(self.onCompletionActivated)
        
        self.updateRequest.connect(self.onUpdateRequest)
        self.textChanged.connect(self.onTextChanged)
        self.selectionChanged.connect(self.onSelectionChanged)
        
        self.document().contentsChange.connect(self.onContentChange)
        
    def changeAutocomplete(self, autocomplete):
        print("textField changeAutocomplete")
        self._completerItemModel.changeAutocomplete(autocomplete)
        
    def onCompletionActivated(self, completion): # QString
        pass

    def insertTextAt(self, position, text):
        cursor = QtGui.QTextCursor(self.document())
        cursor.setPosition(position, QtGui.QTextCursor.MoveAnchor)
        cursor.insertText(text)
        
    def removeTextAt(self, position, length):
        cursor = QtGui.QTextCursor(self.document())
        cursor.setPosition(position, QtGui.QTextCursor.MoveAnchor)
        while length > 0:
            cursor.deletePreviousChar()
            length -= 1

    def indentIn(self):
        cursor = self.textCursor()
        anchor = cursor.anchor()
        position = cursor.position()
        
        doc = self.document()
        text = doc.toPlainText();
        
        if anchor == position:
            column = 0
            while position - column - 1 >= 0 and text[position - column - 1] != "\n":
                column += 1
            cursor.insertText(''.ljust(4 - (column % 4)))
        else:
            if anchor > position:
                [anchor, position] = [position, anchor]
                
            editCursor = QtGui.QTextCursor(doc)
            
            block = doc.findBlock(anchor)
            #editCursor.setPosition(block.position())
            #editCursor.insertText(''.ljust(4))
            
            while block.position() < position:
                editCursor.setPosition(block.position())
                editCursor.insertText(''.ljust(4))
                block = block.next()

    def indentOut(self):
        cursor = self.textCursor()
        anchor = cursor.anchor()
        position = cursor.position()
        
        doc = self.document()
        text = doc.toPlainText();
        
        if anchor == position:
            while position > 0 and text[position - 1] != "\n":
                position -= 1
            lineLength = cursor.position() - position
            overlapping = lineLength % 4
            if overlapping == 0:
                overlapping = 4
            while doc.characterAt(cursor.position() - 1) == " ":
                cursor.deletePreviousChar()
                overlapping -= 1
                if overlapping <= 0:
                    break
        else:
            if anchor > position:
                [anchor, position] = [position, anchor]
                
            editCursor = QtGui.QTextCursor(doc)
            
            block = doc.findBlock(anchor)
            #editCursor.setPosition(block.position())
            #for i in range(0, 4):
            #    editCursor.deleteChar()
            
            while block.position() < position:
                editCursor.setPosition(block.position())
                for i in range(0, 4):
                    editCursor.deleteChar()
                block = block.next()
 
    def deleteCurrentLines(self):
        cursor = self.textCursor()
        anchor = cursor.anchor()
        position = cursor.position()
        text = self.document().toPlainText();
        
        if anchor == position:
            while position < len(text) and text[position] != "\n":
                position += 1
            cursor.setPosition(position)
            cursor.deletePreviousChar()
            while text[cursor.position()] != "\n":
                cursor.deletePreviousChar()
        else:
            print("*delete line*")
            print("*multiline*")

    def onUpdateRequest(self, rect, dy):
        # print([rect, dy])
        self.parent.onUpdate(rect, dy)
        
    def onTextChanged(self):
        self.parent.onTextChanged()

    def onSelectionChanged(self):
        self._selectionChangeCounter += 1
        cursor = self.textCursor()
        anchor = cursor.anchor()
        position = cursor.position()
        text = cursor.selectedText()
        
        currentTextChangeCounter = self._selectionChangeCounter
        QTimer.singleShot(50, lambda: self._checkSelectionChanged(
            currentTextChangeCounter, 
            position, 
            anchor, 
            text
        ))
        
    def _checkSelectionChanged(self, selectionChangeCounter, position, anchor, text):
        if selectionChangeCounter == self._selectionChangeCounter:
            self.parent.onSelectionChanged(position, anchor, text)

    def onContentChange(self, position, removed, added):
        # print([position, removed, added])

        if added > 0:
            self.parent.onTextInserted( 
                self.document().toPlainText(),
                position,
                added
            )
        
    def contentWidth(self):
        doc = self.document()
        block = doc.firstBlock()
        lastBlock = doc.lastBlock()
        biggestWidth = 0
        while type(block) is QtGui.QTextBlock:
            width = len(block.text()) * 10
            # print([width])
            # width = self.blockBoundingRect(block).width()
            if width > biggestWidth:
                biggestWidth = width
            if block == lastBlock:
                break
            block = block.next()
        return biggestWidth + 24
        
    def contentHeight(self):
        doc = self.document()
        block = doc.firstBlock()
        charHeight = self.blockBoundingRect(block).height()
        return doc.lineCount() * charHeight + 32

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Tab:
            self.indentIn()
            return True
        if event.key() == QtCore.Qt.Key_Backtab:
            self.indentOut()
            return True
        return super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        return super().keyReleaseEvent(event)
