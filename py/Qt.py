
import sys

from typing import Self, Callable
from PySide6.QtCore import SignalInstance

from py.Hub import Log

class SafeHandler:
    _instances: list[Self] = []
    
    def __init__(self, event: SignalInstance, handler: Callable) -> None:
        SafeHandler._instances.append(self)
        self.handler = handler
        event.connect(self.receive)
         
    def receive(self, *args: list) -> None:
        try:
            self.handler(*args)
        except:
            exception = sys.exc_info()[1]
            Log.error(exception) 
         
def connect_safely(event: SignalInstance, handler: Callable):
    SafeHandler(event, handler)
  
   