
from PySide6 import QtCore, QtWidgets, QtGui
from os.path import basename, dirname, abspath
from PySide6.QtCore import QTimer
import subprocess
import os
import hashlib

from py.TextField import TextField
from py.LineNumbers import LineNumbers
from py.MessageBroker import MessageBroker
from py.Languages.LanguageSelector import LanguageSelector
from py.Languages.Language import Language

class EditorWindow(QtWidgets.QMainWindow): # QWidget

    def __init__(self, filePath = None):
        super(EditorWindow, self).__init__()
        
        self.lineNumbers = LineNumbers(self)
        self.textField = TextField(self)
        
        self.messageBroker = None
        
        if filePath != None:
            self.openFile(filePath)
        else:
            self.closeFile()

        self.centralWidget = QtWidgets.QWidget()
        self.centralWidget.layout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.centralWidget.layout.setSpacing(0)
        self.centralWidget.layout.setContentsMargins(0, 0, 0, 0)
        self.centralWidget.layout.addWidget(self.lineNumbers, 0)
        self.centralWidget.layout.addWidget(self.textField, 0)
        self.setCentralWidget(self.centralWidget)
        
        self._initMenu()
        
        firstUpdate = QTimer()
        firstUpdate.setInterval(10)
        firstUpdate.timeout.connect(self.onTextChanged)
        firstUpdate.start()
        
    def closeFile(self):
        self.filePath = None
        self.setWindowTitle("[No file] - qtEdit")
        self.hashOnDisk = ""
        self.lengthOnDisk = 0
        
    def openFile(self, filePath):
        self.filePath = abspath(filePath)
        self.messageBroker = MessageBroker(self)
        
        document = self.textField.document()
        
        selector = LanguageSelector()
        self.language = selector.selectForFilePath(self.filePath)
        
        handle = open(self.filePath, "r")
        text = handle.read()

        if self.language != None:
            assert isinstance(self.language, Language)
            self.syntaxTree = self.language.parse(text)
            self.highlighter = self.language.syntaxHighlighter(document, self.syntaxTree)
        
        self.hashOnDisk = hashlib.md5(text.encode()).hexdigest()
        self.lengthOnDisk = len(text)
        
        document.setPlainText(text)
        
        self.updateTitle()
        
    def saveFile(self):
        text = self.textField.document().toPlainText()
        
        handle = open(self.filePath, "w")
        handle.write(text)
        self.hashOnDisk = hashlib.md5(text.encode()).hexdigest()
        self.lengthOnDisk = len(text)
        self.updateTitle()

    def updateTitle(self):
        text = self.textField.document().toPlainText()
        textHash = hashlib.md5(text.encode()).hexdigest()
        modified = (len(text) != self.lengthOnDisk) or (textHash != self.hashOnDisk)

        if modified:
            self.setWindowTitle("* %s (%s) - qtEdit" % (
                basename(self.filePath), 
                dirname(self.filePath)
            ))
        else:
            self.setWindowTitle("%s (%s) - qtEdit" % (
                basename(self.filePath), 
                dirname(self.filePath)
            ))
        
    def presentSelf(self):
        self.activateWindow()
        self.setFocus()
        
    def onUpdate(self, rect, dy):
        self.lineNumbers.onUpdate(rect, dy)
        
    def onTextChanged(self):
        self.updateTitle()
        contentWidth = self.textField.contentWidth()
        contentHeight = self.textField.contentHeight()
        
        contentWidth = min(contentWidth, 800)
        contentHeight = min(contentHeight, 800)
        
        contentWidth = max(contentWidth, 275)
        contentHeight = max(contentHeight, 150)
        
        print([contentWidth, contentHeight])
        
        self.setMinimumWidth(contentWidth)
        self.setMinimumHeight(contentHeight)
        
        if contentWidth >= 800:
            contentWidth = 16777215
        
        if contentHeight >= 800:
            contentHeight = 16777215
            
        self.setMaximumWidth(contentWidth)
        self.setMaximumHeight(contentHeight)
        
        afterUpdate = QTimer()
        afterUpdate.setInterval(10)
        afterUpdate.timeout.connect(self._afterTextChanged)
        afterUpdate.start()
        
    def showOpenFilePicker(self):
        print('showOpenFilePicker')
        
        (filePath, fileTypeDescr) = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Open File", 
            dirname(self.filePath),
            "Text files (*.*)"
        )
        
        print(filePath)
        
        bashScript = "/home/gerrit/workspace/Privat/qtEdit/run.sh"
        
        os.system(f"nohup {bashScript} '{filePath}' 2>&1 > {bashScript}.log")
        
    def _afterTextChanged(self):
        self.setMinimumWidth(0)
        self.setMinimumHeight(0)
        self.setMaximumWidth(16777215)
        self.setMaximumHeight(16777215)
        
    def _initMenu(self):
        
        menuBar = self.menuBar()
        
        fileMenu = menuBar.addMenu('File')
        
        openAction = fileMenu.addAction('Open')
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open')
        openAction.triggered.connect(self.showOpenFilePicker)
        
        saveAction = fileMenu.addAction('Save')
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save')
        saveAction.triggered.connect(self.saveFile)
        
        quitAction = fileMenu.addAction('Quit')
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit')
        quitAction.triggered.connect(self.close)
        
        self.setMenuBar(menuBar)
        
        menuBar.show()
        
