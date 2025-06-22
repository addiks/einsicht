
import sys, os, traceback, logging

from systemd.journal import JournalHandler

from os.path import basename, dirname, abspath

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import QTimer

from py.EditorWindow import EditorWindow
from py.MessageBroker import MessageBroker, FileAlreadyOpenOnOtherProcessException
from py.Versioning.VersioningSelector import VersioningSelector


class Application(QtWidgets.QApplication):
    _instance = None

    @staticmethod
    def main(argv):
        try:
            app = Application.instance()
            try:
                return app.run(argv)
                
            except FileAlreadyOpenOnOtherProcessException:
                return 0
        
            except Exception as exception:
                app.error(exception)
                app.error(traceback.format_exc())
                
        except Exception as exception:
            print(exception)
            print(traceback.format_exc())
        return -2
        
    @staticmethod
    def instance():
        if Application._instance == None:
            Application._instance = Application()
        return Application._instance
        
    def __init__(self):
        super().__init__([])
        self.setApplicationDisplayName("Einsicht - 1s")
        self.setDesktopFileName("einsicht")
        
        self.logger = logging.getLogger('einsicht')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(JournalHandler(SYSLOG_IDENTIFIER='einsicht'))
        
        self._versioningSelector = VersioningSelector()
        self.messageBroker = None
        
        self._textChangeCounter = 0
        
        self._reset()
        self.window = EditorWindow(self)

        QTimer.singleShot(10, lambda: self.onFileContentChanged(force=True))
        
    def _reset(self):
        self.fileContent = ""
        self.filePath = None
        self.hashOnDisk = ""
        self.lengthOnDisk = 0
        self.language = None
        self.versioning = None
        self.projectIndex = None
        self.tokens = None
        self.syntaxTree = None
        self.highlighter = None
            
    def run(self, argv):
        filePath = None
        if len(sys.argv) > 1:
            filePath = abspath(sys.argv[1])
        
        if filePath != None:
            self.openFile(filePath)
            self.info("Opened file '" + filePath + "'")
        else:
            self._reset()
            self.window.onFileClosed()
            self.info("Opened empty file")

        self.window.show()
        
        exitCode = self.exec() # Qt execution loop
        
        self.info("Qt exited with code " + str(exitCode))
    
        return exitCode
                
    def closeFile(self):
        self._reset()
        self.window.onFileClosed()
        self.info("Closed file")
        
    def openFile(self, filePath):
        self.filePath = abspath(filePath)
        self.messageBroker = MessageBroker(self)
        
        document = self.textField.document()
        
        selector = LanguageSelector()
        self.language = selector.selectForFilePath(self.filePath)
        
        with open(self.filePath, "r") as handle:
            self.fileContent = handle.read()

        self.syntaxTree = None
        self.highlighter = None
        if self.language != None:
            assert isinstance(self.language, Language)
            (self.syntaxTree, self.tokens) = self.language.parse(self.fileContent, None, None)
            self.highlighter = self.language.syntaxHighlighter(document, self.syntaxTree)
        
        self.versioning = self._versioningSelector.selectVersioningFor(self.filePath)
        
        self.projectIndex = None
        if self.versioning != None:
            self.projectIndex = ProjectIndex(self.versioning.metaFolder() + "/einsicht.db")
        
        self.hashOnDisk = hashlib.md5(self.fileContent.encode()).hexdigest()
        self.lengthOnDisk = len(self.fileContent)
        
        document.setPlainText(self.fileContent)
        
        self.window.onFileOpened()
        
    def saveFile(self):
        self.info("open(" + self.filePath + ")")
        try:
            with open(self.filePath, "w") as handle:
                self.info("write(" + str(len(self.fileContent)) + ")")
                handle.write(self.fileContent)
                self.hashOnDisk = hashlib.md5(self.fileContent.encode()).hexdigest()
                self.lengthOnDisk = len(self.fileContent)
            self.window.updateTitle()
            self.info("Saved file '%s'" % self.filePath)
            self._updateProjectIndex()
            self.info("Updated project index")
        except:
            e = sys.exc_info()[0]
            self.info("While saving file: %s" % e)
            raise
            
    def _updateProjectIndex(self):
        if self.syntaxTree != None and self.projectIndex != None:
            context = FileContext(
                self.filePath, 
                self.versioning.projectRoot(), 
                self.syntaxTree,
                self.language
            )
            
            self.language.populateFileContext(context)
            self.projectIndex.storeFileContext(context)
                 
    def isModified(self):
        textHash = hashlib.md5(self.fileContent.encode()).hexdigest()
        modified = (len(self.fileContent) != self.lengthOnDisk) or (textHash != self.hashOnDisk)
        return modified
        
    def onFileContentChanged(self, force=False):
        doc = self.window.textField.document()
        fileContent = doc.toPlainText()
        
        if fileContent == self.fileContent and not force:
            return
        
        self._textChangeCounter += 1
        
        self.fileContent = fileContent
        self.window.onTextChanged()

        currentTextChangeCounter = self._textChangeCounter
        
        QTimer.singleShot(10, self.window.afterTextChanged)
        QTimer.singleShot(250, lambda: self._checkStoppedTyping(currentTextChangeCounter))
           
    def _checkStoppedTyping(self, textChangeCounter):
        if textChangeCounter == self._textChangeCounter:
            self.onStoppedTyping()
            self.window.onStoppedTyping()
        self._checkAutocompleteTrigger()
        
            
    def onStoppedTyping(self):
        if self.language != None:
            (self.syntaxTree, self.tokens) = self.language.parse(
                self.fileContent, 
                self.filePath,
                self.syntaxTree, 
                self.tokens
            )
            self.window.onNewSyntaxTree()
               
    def _checkAutocompleteTrigger(self):
        if self.tokens != None and self.projectIndex != None:
            cursorPosition = self.textField.textCursor().position()
            
            autocompletion = Autocompletion(
                self.language,
                self.projectIndex,
                self.tokens,
                self.syntaxTree,
                cursorPosition
            )
         
            self.window.changeAutocomplete(autocompletion)
            
    def showOpenFilePicker(self):
        (filePath, fileTypeDescr) = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Open File", 
            dirname(self.filePath),
            "Text files (*.*)"
        )
        
        bashScript = self._bashScript()
        os.system(f"nohup {bashScript} '{filePath}' > {bashScript}.log 2>&1 &")
        
    def newFile(self):
        bashScript = self._bashScript()
        os.system(f"nohup {bashScript} > {bashScript}.log 2>&1 &")
        
    def fileNameDescription(self):
        if self.filePath == None:
            return "[no file]"
        else:
            return basename(self.filePath)
        
    def _bashScript(self):
        return self.baseDir() + "/bin/1s.sh"
        
    def info(self, message):
        self.logger.info(self.fileNameDescription() + ' - ' + message)
        
    def error(self, message):
        self.logger.error(self.fileNameDescription() + ' - ' + message)
        
        
    def baseDir(self):
        return dirname(dirname(abspath(__file__)))
        