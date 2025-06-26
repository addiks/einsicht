
from os import path

from .GitVersioning import GitVersioning

from py.Versioning import Versioning
from py.Hub import Log

type OptionalVersioning = Versioning | None

class VersioningSelector:
    
    def selectVersioningFor(self, filePath: str) -> OptionalVersioning:
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
          