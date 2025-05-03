
import os, sys, traceback
from PySide6 import QtCore, QtWidgets, QtGui

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from py.ProjectIndex import ProjectIndex
from py.Languages.LanguageSelector import LanguageSelector
from py.Widgets.ReIndexWindow import ReIndexWindow

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("\n USAGE: rebuild-index.py [INDEX-FILE] [FOLDER-TO-INDEX]")
        sys.exit(-1)

    indexFile = sys.argv[1]
    pathToIndex = sys.argv[2]
    app = QtWidgets.QApplication([])
    
    try:
        index = ProjectIndex(indexFile)
        
        window = ReIndexWindow()
        window.show()
        
        index.clear()
        
        if os.path.isdir(pathToIndex):
            index.indexFolder(pathToIndex, pathToIndex)
            
        elif os.path.isfile(pathToIndex):
            index.indexFile(pathToIndex, os.path.dirname(pathToIndex))
        
        #print("*app.exec*")
        #sys.exit(app.exec())
        
    except Exception as exception:
        print(exception)
        print(traceback.format_exc())
        sys.exit(-2)