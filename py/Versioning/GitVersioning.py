
import os

from .Versioning import Versioning

class GitVersioning(Versioning):
    def __init__(self, projectRoot):
        self._projectRoot = projectRoot

    def name(self):
        return "Git"
    
    def projectRoot(self):
        return self._projectRoot
    
    def status(self):
        return ""
        
    def openUI(self):
        os.system(f"git gui")
        
