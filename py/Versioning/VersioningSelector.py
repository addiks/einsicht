
from os import path

from .GitVersioning import GitVersioning

from py.Log import Log

class VersioningSelector:
    
    def selectVersioningFor(self, filePath):
        versioning = None
        directoryPath = path.dirname(filePath)
        while path.isdir(directoryPath) and directoryPath != "/":
            directoryPath = path.dirname(directoryPath)
            metaFolder = directoryPath + "/.git"
            if path.isdir(metaFolder):
                versioning = GitVersioning(directoryPath, metaFolder)
                break
        Log.debug("Selected versioning " + str(type(versioning)))
        return versioning
          