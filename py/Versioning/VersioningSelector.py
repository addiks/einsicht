
from os import path

from .GitVersioning import GitVersioning

from py.Versioning import Versioning
from py.Hub import Log, Hub

type OptionalVersioning = Versioning | None

class VersioningSelector:

    def __init__(self, hub: Hub):
        self.hub = hub
    
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
        self.hub.register(versioning)
        return versioning
          