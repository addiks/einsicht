
import sys, os, traceback, logging, hashlib

from systemd.journal import JournalHandler
from typing import Any, Self
from os.path import basename, dirname, abspath

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QTimer

from py.Widgets.EditorWindow import EditorWindow
from py.MessageBroker import MessageBroker, FileAlreadyOpenOnOtherProcessException
from py.Versioning.VersioningSelector import VersioningSelector

from py.Languages.LanguageSelector import LanguageSelector
from py.Versioning.VersioningSelector import VersioningSelector
from py.ProjectIndex import ProjectIndex
from py.Languages.Language import Language
from py.Languages.Language import FileContext
from py.Autocomplete.Autocompletion import Autocompletion
from py.Hub import Hub, Log
from py.Api import FileAccess

class Application(QtWidgets.QApplication, FileAccess):
    _instance = None

    @staticmethod
    def main(argv: list[str]) -> int:
        try:
            app = Application.instance()
            return app.run(argv)
            
        except FileAlreadyOpenOnOtherProcessException:
            return 0
    
        except:
            exception = sys.exc_info()[0]
            Log.error(exception)
            Log.error(traceback.format_exc())
            
        return -2
        
    @staticmethod
    def instance() -> Self:
        if Application._instance == None:
            Application._instance = Application()
        return Application._instance
        
    def __init__(self):
        super().__init__([])
        self.setApplicationDisplayName("Einsicht - 1s")
        self.setDesktopFileName("einsicht")
        
        self.hub = Hub()
        self.hub.register(self)
        
        self._textChangeCounter = 0
        
        self._reset()
        self.window = EditorWindow(self, self.hub)
        self.messageBroker = None
        self._versioningSelector = VersioningSelector(self.hub)
        
        QTimer.singleShot(10, lambda: self.onFileContentChanged(force=True))
        
    def _reset(self) -> None:
        self._fileContent = ""
        self._filePath = None
        self.hashOnDisk = ""
        self.lengthOnDisk = 0
        self.language = None
        self.versioning = None
        self.projectIndex = None
        self.tokens = None
        self.syntaxTree = None
        self.highlighter = None
        Log.setPrefix(self.fileNameDescription())
            
    def run(self, argv: list[str]) -> int:
        filePath = None
        if len(sys.argv) > 1:
            filePath = abspath(sys.argv[1])
        
        if filePath != None:
            self.openFile(filePath)
            Log.info("Opened file '" + filePath + "'")
        else:
            self._reset()
            self.window.onFileClosed()
            Log.info("Opened empty file")

        self.window.show()
        
        exitCode = self.exec() # Qt execution loop
        
        Log.info("Qt exited with code " + str(exitCode))
    
        return exitCode
                
    def closeFile(self) -> None:
        self._reset()
        self.window.onFileClosed()
        self.info("Closed file")
        
    def openFile(self, filePath: str) -> None:
        self._filePath = abspath(filePath)
        
        Log.setPrefix(self.fileNameDescription() + ' - ')
        self.messageBroker = MessageBroker(self, self.hub)
        document = self.window.textField.document()
        
        selector = LanguageSelector(self.hub)
        self.language = selector.selectForFilePath(self._filePath)
        
        with open(self._filePath, "r") as handle:
            self._fileContent = handle.read()
            Log.debug("Read " + str(len(self._fileContent)) + " bytes")

        self.syntaxTree = None
        self.highlighter = None
        if self.language != None:
            assert isinstance(self.language, Language)
            (self.syntaxTree, self.tokens) = self.language.parse(self._fileContent, None, None)
            self.highlighter = self.language.syntaxHighlighter(document, self.syntaxTree)
        
        self.versioning = self._versioningSelector.selectVersioningFor(self._filePath)
        
        self.projectIndex = None
        if self.versioning != None:
            self.projectIndex = ProjectIndex(self.versioning.metaFolder() + "/einsicht.db")
        
        self.hashOnDisk = hashlib.md5(self._fileContent.encode()).hexdigest()
        self.lengthOnDisk = len(self._fileContent)
        
        document.setPlainText(self._fileContent)
        
        self.window.onFileOpened()
        
    def saveFile(self) -> None:
        try:
            with open(self._filePath, "w") as handle:
                handle.write(self._fileContent)
                self.hashOnDisk = hashlib.md5(self._fileContent.encode()).hexdigest()
                self.lengthOnDisk = len(self._fileContent)
            self.window.updateTitle()
            Log.debug("Saved file '%s'" % self._filePath)
            self._updateProjectIndex()
            Log.debug("Updated project index")
        except:
            Log.error("While saving file: %s" % Log.normalize(sys.exc_info()[1]))
            raise
            
    def _updateProjectIndex(self) -> None:
        if self.syntaxTree != None and self.projectIndex != None:
            context = FileContext(
                self._filePath, 
                self.versioning.projectRoot(), 
                self.syntaxTree,
                self.language
            )
            
            self.language.populateFileContext(context)
            self.projectIndex.storeFileContext(context)
                 
    def isModified(self) -> bool:
        textHash = hashlib.md5(self._fileContent.encode()).hexdigest()
        modified = (len(self._fileContent) != self.lengthOnDisk) or (textHash != self.hashOnDisk)
        return modified
        
    def filePath(self) -> str:
        return self._filePath
        
    def fileContent(self) -> str:
        return self._fileContent
        
    def onFileContentChanged(self, force: bool = False) -> None:
        doc = self.window.textField.document()
        fileContent = doc.toPlainText()
        
        if fileContent == self._fileContent and not force:
            return
        
        self._textChangeCounter += 1
        
        self._fileContent = fileContent
        self.window.onTextChanged()

        currentTextChangeCounter = self._textChangeCounter
        
        QTimer.singleShot(10, self.window.afterTextChanged)
        QTimer.singleShot(250, lambda: self._checkStoppedTyping(currentTextChangeCounter))
           
    def _checkStoppedTyping(self, textChangeCounter: int) -> None:
        if textChangeCounter == self._textChangeCounter:
            self.onStoppedTyping()
            self.window.onStoppedTyping()
        self._checkAutocompleteTrigger()
        
            
    def onStoppedTyping(self) -> None:
        if self.language != None:
            (self.syntaxTree, self.tokens) = self.language.parse(
                self._fileContent, 
                self._filePath,
                self.syntaxTree, 
                self.tokens
            )
            self.window.onNewSyntaxTree()
               
    def _checkAutocompleteTrigger(self) -> None:
        if self.tokens != None and self.projectIndex != None:
            cursorPosition = self.window.textField.textCursor().position()
            
            autocompletion = Autocompletion(
                self.language,
                self.projectIndex,
                self.tokens,
                self.syntaxTree,
                cursorPosition
            )
         
            self.window.changeAutocomplete(autocompletion)
            
    def showOpenFilePicker(self):
        Log.debug("FOO")
        (filePath, fileTypeDescr) = QtWidgets.QFileDialog.getOpenFileName(
            self.window, 
            "Open File", 
            dirname(self._filePath),
            "Text files (*.*)"
        )
        
        bashScript = self._bashScript()
        os.system(f"nohup {bashScript} '{filePath}' > {bashScript}.log 2>&1 &")
        
    def newFile(self) -> None:
        bashScript = self._bashScript()
        os.system(f"nohup {bashScript} > {bashScript}.log 2>&1 &")
        
    def fileNameDescription(self) -> str:
        if self._filePath == None:
            return "[no file]"
        else:
            return basename(self._filePath)
        
    def _bashScript(self) -> str:
        return self.baseDir() + "/bin/1s.sh"
        
    def baseDir(self) -> str:
        return dirname(dirname(abspath(__file__)))
        
