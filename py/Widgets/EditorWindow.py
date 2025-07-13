
from PySide6 import QtCore, QtWidgets, QtGui
from os.path import basename, dirname, abspath
from PySide6.QtCore import QTimer

import subprocess
import os
import hashlib
import re
import traceback
import logging
from systemd.journal import JournalHandler

from py.Widgets.TextField import TextField
from py.Widgets.LineNumbers import LineNumbers
from py.Widgets.AutocompleteWidget import AutocompleteWidget
from py.Widgets.SearchBar import SearchBar
from py.MessageBroker import MessageBroker
from py.Languages.LanguageSelector import LanguageSelector
from py.Languages.Language import Language, LanguageFromSyntaxTreeHighlighter
from py.Languages.Language import FileContext
from py.Languages.AbstractSyntaxTree import ASTRoot
from py.Versioning import Versioning
from py.Versioning.VersioningSelector import VersioningSelector
from py.ProjectIndex import ProjectIndex
from py.Autocomplete.Autocompletion import Autocompletion, AutocompletionOffer
from py.Qt import connect_safely
from py.Hub import Log, Hub, on
from py.Api import FileAccess
from py.MessageBroker import MessageBroker

class EditorWindow(QtWidgets.QMainWindow): # QWidget

    def __init__(self, hub: Hub):
        super(EditorWindow, self).__init__() 
        self.hub = hub
        
        hub.setup(self)
        
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(
            hub.get(FileAccess).baseDir() + "/resources/einsicht-logo-v1.512.png"
        )))
        
        self.lineNumbers = LineNumbers(self, hub)
        self.textField = TextField(self, hub)
        self._textChangeCounter = 0
        
        self.highlighter = None
        self.messageBroker = None
        self._autocompleteWidget = AutocompleteWidget(self, hub, None)
        
        self.centralWidget = QtWidgets.QWidget()

        vbox = QtWidgets.QVBoxLayout(self.centralWidget)
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        hboxWidget = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout(hboxWidget)
        hboxWidget.layout = hbox
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(self.lineNumbers, 0)
        hbox.addWidget(self.textField, 0)
        
        self.searchBar = SearchBar(hub);
        
        vbox.addWidget(self.searchBar)
        vbox.addWidget(hboxWidget)
        self.centralWidget.layout = vbox
        self.setCentralWidget(self.centralWidget)
        
        self._initMenu()
        
    @on(TextField.onTextChanged)
    def _onTextChanged(self):
        self.updateTitle()
        self._updateDimensions()
        
    @on(FileAccess.closeFile)
    def onFileClosed(self):
        self.setWindowTitle("[No file] - Einsicht")
        self.highlighter = None
        
    @on(MessageBroker.presentSelf)
    def presentSelf():
        self.activateWindow()
        self.setFocus()
    
    def onFileOpened(self):
        self.updateTitle()
        document = self.textField.document()
        document.setPlainText(self.hub.get(FileAccess).fileContent())
        
    def updateTitle(self):
    
        file = self.hub.get(FileAccess)
        filePath = file.filePath()
        Log.debug("file.isModified(): " + str(file.isModified()))
        if filePath == None:
            self.setWindowTitle("[No file]")
        elif file.isModified():
            self.setWindowTitle("* %s (%s)" % (
                basename(filePath), 
                dirname(filePath)
            ))
        else:
            self.setWindowTitle("%s (%s)" % (
                basename(filePath), 
                dirname(filePath)
            ))
        
    def onUpdate(self, rect, dy):
        self.lineNumbers.onUpdate(rect, dy)
        
        # self._autocompleteWidget.hide()
        
    def afterTextChanged(self):
        self.setMinimumWidth(0)
        self.setMinimumHeight(0)
        self.setMaximumWidth(16777215)
        self.setMaximumHeight(16777215)
              
    @on(AutocompletionOffer)
    def applyAutocompleOffer(self, offer):
        self.hub.get(AutocompletionOffer).applyToTextField(self.textField)
        
    def isAutocompleteVisible(self):
        return self._autocompleteWidget.isVisible()
        
    def focusAutocompleteWidget(self):  
        self._autocompleteWidget.setFocus()
        
    def changeAutocomplete(self, autocompletion):
        self._autocompleteWidget.changeAutocomplete(autocompletion)
            
    def _updateDimensions(self):
        textField = self.hub.get(TextField)
    
        contentWidth = textField.contentWidth()
        contentHeight = textField.contentHeight()
        
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
        
        QTimer.singleShot(10, self.afterTextChanged)

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
               
    def _toggleFileSearch(self):
        print("*_toggleFileSearch*")
        self.searchBar.toggle()
        
    def _initMenu(self):
        
        menuBar = self.menuBar()

        ########
        ### FILE
        fileMenu = menuBar.addMenu('File')
        
        fileHandler = self.hub.get(FileAccess)
        
        newAction = fileMenu.addAction('New')
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New')
        connect_safely(newAction.triggered, fileHandler.newFile)
        
        openAction = fileMenu.addAction('Open')
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open')
        connect_safely(openAction.triggered, fileHandler.showOpenFilePicker)
        
        saveAction = fileMenu.addAction('Save')
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save')
        connect_safely(saveAction.triggered, fileHandler.saveFile)
        
        saveAsAction = fileMenu.addAction('Save As')
        saveAsAction.setShortcut('Ctrl+Shift+S')
        saveAsAction.setStatusTip('Save')
        connect_safely(saveAsAction.triggered, fileHandler.saveFileAs)
        
        quitAction = fileMenu.addAction('Quit')
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit')
        connect_safely(quitAction.triggered, fileHandler.closeFile)
        
        ########
        ### EDIT
        editMenu = menuBar.addMenu('Edit')
        
        deleteLineAction = editMenu.addAction('Delete line')
        deleteLineAction.setShortcut('Ctrl+D')
        connect_safely(deleteLineAction.triggered, self.textField.deleteCurrentLines)

        indentInAction = editMenu.addAction('Indent in')
        connect_safely(indentInAction.triggered, self.textField.indentIn)

        indentOutAction = editMenu.addAction('Indent out')
        connect_safely(indentOutAction.triggered, self.textField.indentOut)

        replaceInFileAction = editMenu.addAction('Search and Replace')
        
        ##########
        ### SEARCH
        searchMenu = menuBar.addMenu('Search')
        
        searchInFileAction = searchMenu.addAction('Search in this File')
        searchInFileAction.setShortcut('Ctrl+F')
        connect_safely(searchInFileAction.triggered, self._toggleFileSearch)
        
        searchInOpenFilesAction = searchMenu.addAction('Search in all open Files')
        searchInOpenFilesAction.setShortcut('Ctrl+Shift+F')
        
        searchInProjectAction = searchMenu.addAction('Search in Project-Index')
        searchInProjectAction.setShortcut('Ctrl+Alt+F')
        
        ##############
        ### VERSIONING
        
        self.versioningMenu = menuBar.addMenu('Versioning')
        self.versioningGuiAction = self.versioningMenu.addAction('Open UI')
        
        def onVersioningChange():
            if self.hub.has(Versioning):
                self.versioningMenu.setTitle(self.hub.get(Versioning).name())
                self.versioningMenu.setVisible(True)
                self.versioningGuiAction.setEnabled(True)
                connect_safely(self.versioningGuiAction.triggered, self.hub.get(Versioning).openUI)
            else:
                self.versioningMenu.setTitle('Versioning')
                self.versioningMenu.setVisible(False)
            self.versioningGuiAction.setEnabled(False)
        self.hub.on(Versioning, onVersioningChange)
       
        #############
        ### DEBUGGING
        debuggingMenu = menuBar.addMenu('Debugging')
        
        self.setMenuBar(menuBar)
        
        menuBar.show()
        
        ############
        ### LANGUAGE
        
        self.languageMenu = menuBar.addMenu("Language")
        def onLanguageChange():
            if self.hub.has(Language):
                self.languageMenu.setTitle(self.hub.get(Language).name())
                self.languageMenu.setVisible(True)
            else:
                self.languageMenu.setTitle("Language")
                self.languageMenu.setVisible(False)
        self.hub.on(Language, onLanguageChange)

        