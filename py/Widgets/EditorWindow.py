
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
from py.Versioning.VersioningSelector import VersioningSelector
from py.ProjectIndex import ProjectIndex
from py.Autocomplete.Autocompletion import Autocompletion
from py.Qt import connect_safely

class EditorWindow(QtWidgets.QMainWindow): # QWidget

    def __init__(self, app):
        super(EditorWindow, self).__init__() 
        self.app = app
        
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap(
            app.baseDir() + "/resources/einsicht-logo-v1.512.png"
        )))
        
        self.lineNumbers = LineNumbers(self, app)
        self.textField = TextField(self, app)
        self._textChangeCounter = 0
        
        self.highlighter = None
        self.messageBroker = None
        self._autocompleteWidget = AutocompleteWidget(self, None)
        
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
        
        self.searchBar = SearchBar(self);
        searchBarLayout = QtWidgets.QHBoxLayout(self.searchBar)
        
        vbox.addWidget(self.searchBar)
        vbox.addWidget(hboxWidget)
        self.centralWidget.layout = vbox
        self.setCentralWidget(self.centralWidget)
        
        self._initMenu()
        
    def onFileClosed(self):
        self.setWindowTitle("[No file] - Einsicht")
        self.highlighter = None
        
    def onFileOpened(self):
        self.updateTitle()
        document = self.textField.document()
        document.setPlainText(self.app.fileContent)
        
        if self.app.language != None:
            self.languageMenu.setTitle(self.app.language.name())
            self.languageMenu.setVisible(True)
        else:
            self.languageMenu.setVisible(False)
            
        if self.app.versioning != None:
            self.versioningMenu.setTitle(self.app.versioning.name())
            self.versioningGuiAction.setEnabled(True)
            connect_safely(self.versioningGuiAction.triggered, self.app.versioning.openUI)
        else:
            self.versioningMenu.setTitle("Versioning")
            self.versioningGuiAction.setEnabled(False)
        
    def updateTitle(self):
        if self.app.filePath == None:
            self.setWindowTitle("[No file]")
        elif self.app.isModified():
            self.setWindowTitle("* %s (%s)" % (
                basename(self.app.filePath), 
                dirname(self.app.filePath)
            ))
        else:
            self.setWindowTitle("%s (%s)" % (
                basename(self.app.filePath), 
                dirname(self.app.filePath)
            ))
        
    def presentSelf(self):
        self.activateWindow()
        self.setFocus()
        
    def onUpdate(self, rect, dy):
        self.lineNumbers.onUpdate(rect, dy)
        
    def onTextChanged(self):
        self.updateTitle()
        self._updateDimensions()
        self.app.onFileContentChanged()
        
        # self._autocompleteWidget.hide()
        
    def afterTextChanged(self):
        self.setMinimumWidth(0)
        self.setMinimumHeight(0)
        self.setMaximumWidth(16777215)
        self.setMaximumHeight(16777215)
        
    def onStoppedTyping(self):
        if isinstance(self.highlighter, LanguageFromSyntaxTreeHighlighter):
            self.highlighter.updateSyntaxTree(self.syntaxTree)
        
    def onNewSyntaxTree(self):
        if isinstance(self.highlighter, LanguageFromSyntaxTreeHighlighter):
            self.highlighter.updateSyntaxTree(self.app.syntaxTree)
                
    def applyAutocompleOffer(self, offer):
        offer.applyToTextField(self.textField)
        
    def isAutocompleteVisible(self):
        return self._autocompleteWidget.isVisible()
        
    def focusAutocompleteWidget(self):  
        self._autocompleteWidget.setFocus()
        
    def changeAutocomplete(self, autocompletion):
        self._autocompleteWidget.changeAutocomplete(autocompletion)
            
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
            
    def _toggleFileSearch(self):
        print("*_toggleFileSearch*")
        self.searchBar.toggle()
        
    def _initMenu(self):
        
        menuBar = self.menuBar()

        ########
        ### FILE
        fileMenu = menuBar.addMenu('File')
        
        newAction = fileMenu.addAction('New')
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New')
        connect_safely(newAction.triggered, self.app.newFile)
        
        openAction = fileMenu.addAction('Open')
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open')
        connect_safely(openAction.triggered, self.app.showOpenFilePicker)
        
        saveAction = fileMenu.addAction('Save')
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save')
        connect_safely(saveAction.triggered, self.app.saveFile)
        
        quitAction = fileMenu.addAction('Quit')
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit')
        connect_safely(quitAction.triggered, self.app.closeFile)
        
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
        if self.app.versioning != None:
            self.versioningMenu = menuBar.addMenu(self.app.versioning.name())
        else:
            self.versioningMenu = menuBar.addMenu('Versioning')
        
        self.versioningGuiAction = self.versioningMenu.addAction('Open UI')
        if self.app.versioning != None:
            self.versioningGuiAction.setEnabled(True)
            connect_safely(self.versioningGuiAction.triggered, self.app.versioning.openUI)
        else:
            self.versioningGuiAction.setEnabled(False)
       
        #############
        ### DEBUGGING
        debuggingMenu = menuBar.addMenu('Debugging')
        
        self.setMenuBar(menuBar)
        
        menuBar.show()
        
        ############
        ### LANGUAGE
        if self.app.language != None:
            self.languageMenu = menuBar.addMenu(self.app.language.name())
        else:
            self.languageMenu = menuBar.addMenu("Language")
            self.languageMenu.setVisible(False)
