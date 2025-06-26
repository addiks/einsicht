
import traceback

from logging import Logger
from typing import Any, Callable

class Application:
    def newFile(self) -> None:
        raise NotImplementedError
        
    def openFile(self, filePath: str) -> None:
        raise NotImplementedError
        
    def saveFile(self) -> None:
        raise NotImplementedError
    
    def closeFile(self) -> None:
        raise NotImplementedError
        
    def fileNameDescription(self) -> str:
        raise NotImplementedError
        
    def isModified(self) -> bool:
        raise NotImplementedError
        
    def onFileContentChanged(self, force: bool = False) -> None:
        raise NotImplementedError
        
    def onStoppedTyping(self) -> None:
        raise NotImplementedError
        
    def baseDir(self) -> str:
        raise NotImplementedError

class Hub:
    def __init__(self):
        self._objects = {}
        self._listeners = {}
        
    def register(self, key: str | type, object: Any) -> None:
        self._objects[key] = object
        
    def registerSingleton(self, object: Any):
        self._objects[type(object)] = object
        
    def get(self, key: str | type) -> Any:
        if key in self._objects:
            return self._objects[key]
        else:
            return None

    def listen(self, event: str, handler: Callable) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(handler)
        
    def dispatch(self, event: str, *args) -> None:
        if event in self._listeners:
            for listener in self._listeners[event]:
                listener(*args)
                
class Log:
    _logger: Logger = None
    _prefix: str = ""

    @staticmethod
    def registerLogger(logger: Logger) -> None:
        Log._logger = logger

    @staticmethod
    def setPrefix(prefix: str) -> None:
        Log._prefix = prefix

    @staticmethod
    def debug(message: Any) -> None:
        message = Log._prepareMessage(message)
        if Log._logger != None:
            Log._logger.debug(message)
        else:
            print(message)
        
    @staticmethod
    def info(message: Any) -> None:
        message = Log._prepareMessage(message)
        if Log._logger != None:
            Log._logger.info(message)
        else:
            print(message)
        
    @staticmethod
    def error(message: Any) -> None:
        message = Log._prepareMessage(message)
        if Log._logger != None:
            Log._logger.error(message)
        print(message)
        
    @staticmethod
    def normalize(target: Any) -> None:
        if isinstance(target, Exception):
            target = "".join(traceback.format_exception(target))
        return target
        
    def _prepareMessage(message: None) -> str:
        message = Log.normalize(message)
        return Log._prefix + str(message)