
import os

from .Versioning import Versioning

class GitVersioning(Versioning):
    def __init__(self, projectRoot, metaFolder):
        self._projectRoot = projectRoot
        self._metaFolder = metaFolder

    def name(self):
        return "Git"
    
    def projectRoot(self):
        return self._projectRoot
    
    def metaFolder(self): # e.g.: the .git folder
        return self._metaFolder
    
    def status(self):
        return ""
        
    def openUI(self):
        os.system(f"git --git-dir=" + self._metaFolder + " --work-tree=" + self._projectRoot + " gui")
        
