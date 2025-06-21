
import sys, os, traceback, logging

from systemd.journal import JournalHandler

from os.path import basename, dirname, abspath

from PySide6 import QtCore, QtWidgets, QtGui

from py.EditorWindow import EditorWindow
from py.MessageBroker import MessageBroker, FileAlreadyOpenOnOtherProcessException


class Application(QtWidgets.QApplication):

    _instance = None

    def __init__(self):
        super().__init__([])
        self.setApplicationDisplayName("Einsicht - 1s")
        self.setDesktopFileName("einsicht")
        
        self.logger = logging.getLogger('einsicht')
        self.logger.addHandler(JournalHandler())
        
        self.filePath = None

    def run(self, argv):
        if len(sys.argv) > 1:
            self.filePath = abspath(sys.argv[1])
        
        window = EditorWindow(self, self.filePath)
        window.show()
        
            
        
    @staticmethod
    def main(argv):
        try:
            app = Application.instance()
        
            app.run(argv)
            
            return app.exec() # Runs Qt execution loop
            
        except FileAlreadyOpenOnOtherProcessException:
            return 0
    
        except Exception as exception:
            print(exception)
        print(traceback.format_exc())
        return -2
        
    @staticmethod
    def instance():
        if Application._instance == None:
            Application._instance = Application()
        return Application._instance
        
    def info(self, message):
        self.logger.info("[%s] %s" % ("ASD", message))
        
    def baseDir(self):
        return dirname(dirname(abspath(__file__)))
        
    def newFile(self):
        bashScript = self.baseDir() + "/bin/1s.sh"
        os.system(f"nohup {bashScript} > {bashScript}.log 2>&1 &")
        