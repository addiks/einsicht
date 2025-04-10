
from PySide6 import QtCore, QtWidgets, QtGui
from os.path import basename, dirname, abspath
from PySide6.QtCore import QTimer

import subprocess
import os
import hashlib
import re
import traceback

from py.Widgets.TextField import TextField
from py.Widgets.LineNumbers import LineNumbers
from py.MessageBroker import MessageBroker
from py.Languages.LanguageSelector import LanguageSelector
from py.Languages.Language import Language, LanguageFromSyntaxTreeHighlighter
from py.Versioning.VersioningSelector import VersioningSelector

class EditorWindow(QtWidgets.QMainWindow): # QWidget

    def __init__(self, filePath = None):
        super(EditorWindow, self).__init__()
        
        self.lineNumbers = LineNumbers(self)
        self.textField = TextField(self)
        self._versioningSelector = VersioningSelector()
        self._textChangeCounter = 0
        
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
        
        QTimer.singleShot(10, lambda: self.onTextChanged(force=True))
        
    def closeFile(self):
        self.fileContent = ""
        self.filePath = None
        self.setWindowTitle("[No file] - adEdit")
        self.hashOnDisk = ""
        self.lengthOnDisk = 0
        self.versioning = None
        self.tokens = None
        self.syntaxTree = None
        
    def openFile(self, filePath):
        self.filePath = abspath(filePath)
        self.messageBroker = MessageBroker(self)
        
        document = self.textField.document()
        
        selector = LanguageSelector()
        self.language = selector.selectForFilePath(self.filePath)
        
        handle = open(self.filePath, "r")
        self.fileContent = handle.read()

        if self.language != None:
            assert isinstance(self.language, Language)
            (self.syntaxTree, self.tokens) = self.language.parse(self.fileContent, None, None)
            self.highlighter = self.language.syntaxHighlighter(document, self.syntaxTree)
        
        self.versioning = self._versioningSelector.selectVersioningFor(self.filePath)
        
        self.hashOnDisk = hashlib.md5(self.fileContent.encode()).hexdigest()
        self.lengthOnDisk = len(self.fileContent)
        
        document.setPlainText(self.fileContent)
        
        self.updateTitle()
        
    def saveFile(self):
        handle = open(self.filePath, "w")
        handle.write(self.fileContent)
        self.hashOnDisk = hashlib.md5(self.fileContent.encode()).hexdigest()
        self.lengthOnDisk = len(self.fileContent)
        self.updateTitle()

    def updateTitle(self):
        textHash = hashlib.md5(self.fileContent.encode()).hexdigest()
        modified = (len(self.fileContent) != self.lengthOnDisk) or (textHash != self.hashOnDisk)

        if modified:
            self.setWindowTitle("* %s (%s) - adEdit" % (
                basename(self.filePath), 
                dirname(self.filePath)
            ))
        else:
            self.setWindowTitle("%s (%s) - adEdit" % (
                basename(self.filePath), 
                dirname(self.filePath)
            ))
        
    def presentSelf(self):
        self.activateWindow()
        self.setFocus()
        
    def onUpdate(self, rect, dy):
        self.lineNumbers.onUpdate(rect, dy)
        
    def onTextChanged(self, force=False):
        doc = self.textField.document()
        fileContent = doc.toPlainText()
        
        if fileContent == self.fileContent and not force:
            return
        
        self._textChangeCounter += 1
        
        self.fileContent = fileContent
        self.updateTitle()
        self._updateDimensions()
        
        currentTextChangeCounter = self._textChangeCounter
        
        QTimer.singleShot(10, self._afterTextChanged)
        QTimer.singleShot(250, lambda: self._checkStoppedTyping(currentTextChangeCounter))
           
    def _afterTextChanged(self):
        self.setMinimumWidth(0)
        self.setMinimumHeight(0)
        self.setMaximumWidth(16777215)
        self.setMaximumHeight(16777215)
        
    def _checkStoppedTyping(self, textChangeCounter):
        if textChangeCounter == self._textChangeCounter:
            self.onStoppedTyping()
            
    def onStoppedTyping(self):
        if self.language != None:
            (self.syntaxTree, self.tokens) = self.language.parse(self.fileContent, self.syntaxTree, self.tokens)
            if isinstance(self.highlighter, LanguageFromSyntaxTreeHighlighter):
                self.highlighter.updateSyntaxTree(self.syntaxTree)
            
            if self.tokens != None:
                cursorPos = self.textField.textCursor().position()
                token = self.tokenAt(cursorPos)
                if token != None:
                    tokenPos = cursorPos - token.offset
                    prefix = token.code[:tokenPos]
                    postfix = token.code[tokenPos:]
                    print([prefix, postfix])
                
        
    def _updateDimensions(self):
        contentWidth = self.textField.contentWidth()
        contentHeight = self.textField.contentHeight()
        
        contentWidth = min(contentWidth, 800)
        contentHeight = min(contentHeight, 800)
        
        contentWidth = max(contentWidth, 275)
        contentHeight = max(contentHeight, 150)
        
        # print([contentWidth, contentHeight])
        
        self.setMinimumWidth(contentWidth)
        self.setMinimumHeight(contentHeight)
        
        if contentWidth >= 800:
            contentWidth = 16777215
        
        if contentHeight >= 800:
            contentHeight = 16777215
            
        self.setMaximumWidth(contentWidth)
        self.setMaximumHeight(contentHeight)

    def onTextInserted(self, text, position, added):
        inserted = text[position:position+added]

        if inserted == "\n":
           lines = text.split("\n")
           lineNumber = text[:position].count("\n")
           
           oldLine = lines[lineNumber]

           indentionMatch = re.match(r'^(\s+)[^\s]?', oldLine)

           if indentionMatch != None:
               indention = indentionMatch.group(1)
               self.textField.insertTextAt(position+added, indention)
               
    def onSelectionChanged(self, position, anchor, text):
        if self.highlighter != None:
            self.highlighter.updateSelection(text)
            
    def showOpenFilePicker(self):
        (filePath, fileTypeDescr) = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Open File", 
            dirname(self.filePath),
            "Text files (*.*)"
        )
        
        bashScript = "/home/gerrit/workspace/Privat/adEdit/bin/adedit.sh"
        
        os.system(f"nohup {bashScript} '{filePath}' > {bashScript}.log 2>&1 &")
        
    def tokenAt(self, position):
        for token in self.tokens:
            if token.offset < position and (token.offset + len(token.code)) >= position:
                return token
        return None
        
    def _toggleFileSearch(self):
        print("*_toggleFileSearch*")
        
    def _initMenu(self):
        
        menuBar = self.menuBar()

        ########
        ### FILE
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
        
        ########
        ### EDIT
        editMenu = menuBar.addMenu('Edit')
        
        deleteLineAction = editMenu.addAction('Delete line')
        deleteLineAction.setShortcut('Ctrl+D')
        deleteLineAction.triggered.connect(self.textField.deleteCurrentLines)

        indentInAction = editMenu.addAction('Indent in')
        indentInAction.triggered.connect(self.textField.indentIn)

        indentOutAction = editMenu.addAction('Indent out')
        indentOutAction.triggered.connect(self.textField.indentOut)

        replaceInFileAction = editMenu.addAction('Search and Replace')
        
        ##########
        ### SEARCH
        searchMenu = menuBar.addMenu('Search')
        
        searchInFileAction = searchMenu.addAction('Search in this File')
        searchInFileAction.setShortcut('Ctrl+F')
        searchInFileAction.triggered.connect(self._toggleFileSearch)
        
        searchInOpenFilesAction = searchMenu.addAction('Search in all open Files')
        searchInOpenFilesAction.setShortcut('Ctrl+Shift+F')
        
        searchInProjectAction = searchMenu.addAction('Search in Project-Index')
        searchInProjectAction.setShortcut('Ctrl+Alt+F')
        
        ##############
        ### VERSIONING
        if self.versioning != None:
            versioningMenu = menuBar.addMenu(self.versioning.name())
            
            versioningGuiAction = versioningMenu.addAction('Open UI')
            versioningGuiAction.triggered.connect(self.versioning.openUI)
        
        #############
        ### DEBUGGING
        debuggingMenu = menuBar.addMenu('Debugging')
        
        self.setMenuBar(menuBar)
        
        menuBar.show()
        
        ############
        ### LANGUAGE
        if self.language != None:
            languageMenu = menuBar.addMenu(self.language.name())
