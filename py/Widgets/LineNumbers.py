
import math 
from PySide6 import QtCore, QtWidgets, QtGui

from py.Hub import Hub
from py.Api import FileAccess, TextField

# https://stackoverflow.com/questions/50074155

class LineNumbers(QtWidgets.QWidget):
    
    def __init__(self, parent: QtWidgets.QWidget, hub: Hub):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.hub = hub
        self.hub.register(self)
        # self.editor.textField.updateRequest.connect(self.update)
        
    def sizeHint(self):
        text = self.hub.get(FileAccess).fileContent()
    	
        lineCount = text.count("\n") + 1
    	
        charWidth = math.ceil(math.log(lineCount + 1, 10))
    
        return QtCore.QSize(charWidth * 10, 0);
        
    def onUpdate(self, rect, dy):
        self.update()
        self.updateGeometry()
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), QtCore.Qt.lightGray)
        
        textField = self.hub.get(TextField)
        
        block = textField.firstVisibleBlock()
        blockNumber = block.blockNumber()
        blockRect = textField.blockBoundingGeometry(block) # QRectF
        
        top = blockRect.translated(textField.contentOffset()).top()
        bottom = top + textField.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QtCore.Qt.black)
                painter.drawText(
                    0, 
                    top, 
                    self.width(),
                    textField.fontMetrics().height(),
                    QtCore.Qt.AlignRight,
                    number
                )
            block = block.next()
            top = bottom
            bottom = top + textField.blockBoundingRect(block).height()
            blockNumber += 1
        
