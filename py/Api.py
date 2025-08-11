
from PySide6 import QtCore, QtWidgets, QtGui

class FileAccess:
    def newFile(self) -> None:
        raise NotImplementedError
        
    def openFile(self, filePath: str) -> None:
        raise NotImplementedError
        
    def saveFile(self) -> None:
        raise NotImplementedError
    
    def closeFile(self) -> None:
        raise NotImplementedError
        
    def fileContent(self) -> str:
        raise NotImplementedError
        
    def fileNameDescription(self) -> str:
        raise NotImplementedError
        
    def isModified(self) -> bool:
        raise NotImplementedError
        
    def onFileContentChanged(self, force: bool = False) -> None:
        raise NotImplementedError
        
    def onStoppedTyping(self) -> None:
        raise NotImplementedError
        
    def filePath(self) -> str:
        raise NotImplementedError

    def baseDir(self) -> str:
        raise NotImplementedError

class TextField:
    def document(self):
        raise NotImplementedError
        
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
        
    def onSelectionChanged(self):
        raise NotImplementedError
        
    def onStoppedTyping(self) -> None:
        raise NotImplementedError
        
    def onTextChanged(self):
        raise NotImplementedError
        
    def onCursorPositionChanged(self):
        raise NotImplementedError
    