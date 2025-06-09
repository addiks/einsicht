
import sys, os, random, traceback
from PySide6 import QtCore, QtWidgets, QtGui
from os.path import basename, dirname, abspath
from PySide6.QtCore import Slot, QObject

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from py.EditorWindow import EditorWindow
from py.MessageBroker import MessageBroker, FileAlreadyOpenOnOtherProcessException


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationDisplayName("Einsicht - 1s")
    app.setDesktopFileName("einsicht")
    
    filePath = None
    
    if len(sys.argv) > 1:
        filePath = abspath(sys.argv[1])
    
    try:
        window = EditorWindow(filePath)
        window.show()
        sys.exit(app.exec())
        
    except FileAlreadyOpenOnOtherProcessException:
        sys.exit(0)

    except Exception as exception:
        print(exception)
        print(traceback.format_exc())
        sys.exit(-2)