
import traceback

from logging import Logger
from typing import Any, Callable

class Hub:
    def __init__(self):
        self._objects: dict[type[T], T] = {}
        self._listeners: dict[str|type, Callable] = {}
        
    def register[T](self, object: T, key: type[T] = None) -> None:
        if key == None:
            key = type(object)
        self._objects[key] = object
        self.notify(key)
        for baseClass in key.__bases__:
            self.register(object, baseClass)
        
    def get[T](self, key: type[T]) -> T:
        if key in self._objects:
            return self._objects[key]
        else:
            return None
            
    def has(self, key: type) -> bool:
        return key in self._objects
        
    def remove(self, key: type) -> None:
        if key in self._objects:
            del self._objects[key]

    def on(self, event: str | type, handler: Callable) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(handler)
        if self.has(event):
            handler()
        
    def notify(self, event: str | type, *args) -> None:
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
        