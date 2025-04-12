
from os import path

from .GitVersioning import GitVersioning

class VersioningSelector:
    
    def selectVersioningFor(self, filePath):
        directoryPath = path.dirname(filePath)
        while path.isdir(directoryPath) and directoryPath != "/":
            directoryPath = path.dirname(directoryPath)
            metaFolder = directoryPath + "/.git"
            if path.isdir(metaFolder):
                return GitVersioning(directoryPath, metaFolder)
        return None
        

