
from os import path

from .GitVersioning import GitVersioning

class VersioningSelector:
    
    def selectVersioningFor(self, filePath):
        directoryPath = path.dirname(filePath)
        while path.isdir(directoryPath) and directoryPath != "/":
            directoryPath = path.dirname(directoryPath)
            if path.isdir(directoryPath + "/.git"):
                return GitVersioning(directoryPath)
        return None
        

