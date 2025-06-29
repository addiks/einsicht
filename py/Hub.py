
import traceback, sys

from logging import Logger
from typing import Any, Self, Callable
from PySide6.QtCore import SignalInstance

class Hub:
    def __init__(self):
        self._objects: dict[type[T], T] = {}
        self._listeners: dict[str|type, list[Callable]] = {}
        
    def register[T](self, object: T, key: type[T] = None) -> None:
        if key == None:
            key = type(object)
        Log.debug("Hub registered " + str(object) + " as " + str(key))
        self._objects[key] = object
        for baseClass in key.__bases__:
            if baseClass != object:
                self.register(object, baseClass)
        self.notify(key)
        
    def get[T](self, key: type[T]) -> T:
        if key in self._objects:
            return self._objects[key]
        else:
            raise Exception("Tried to get unknown object " + str(key) + " from Hub!")
            
    def has(self, key: type) -> bool:
        return key in self._objects
        
    def remove(self, key: type) -> None:
        if key in self._objects:
            del self._objects[key]

    def on(self, event: type | SignalInstance, handler: Callable) -> None:
        if event not in self._listeners:
            self._listeners[event] = []
        Log.debug("Hub listening on " + str(event) + " for handler " + str(handler))
        if isinstance(event, SignalInstance):
            connect_safely(event, handler)
        else:
            self._listeners[event].append(handler)
            if self.has(event) and event != object:
                self._callListener(event, handler, ())
        
    def notify(self, event: type, *args) -> None:
        if not isinstance(event, type) and not isinstance(event, Callable):
            event = type(event)
        Log.debug("Hub was notified about " + str(event) + " (" + str(type(event)) + ")")
        if event in self._listeners:
            for listener in self._listeners[event]:
                self._callListener(event, listener, *args)
                
    def _callListener(self, event: type, listener: Callable, *args):
        try:
            Log.debug("Hub notified " + str(listener) + " about " + str(event))
            listener(*args)
        except:
            exception = sys.exc_info()[0]
            Log.error("Exception while notifying " + str(listener) + " about " + str(event))
            Log.error(exception)
            Log.error(traceback.format_exc())
        
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
        
class SafeHandler:
    _instances: list[Self] = []
    
    def __init__(self, event: SignalInstance, handler: Callable) -> None:
        SafeHandler._instances.append(self)
        self.event = event
        self.handler = handler
        event.connect(self.receive)
         
    def receive(self, *args: list) -> None:
        try:
            Log.debug("Hub notified " + str(self.handler) + " about Qt event " + str(self.event))
            self.handler(*args)
        except:
            exception = sys.exc_info()[1]
            Log.error(exception) 
         
def connect_safely(event: SignalInstance, handler: Callable):
    SafeHandler(event, handler)
  
   