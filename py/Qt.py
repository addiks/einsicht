
import sys
from py.Log import Log

class SafeHandler:
    _instances = []
    
    def __init__(self, event, handler):
        SafeHandler._instances.append(self)
        self.event = event
        self.handler = handler
        event.connect(self.receive)
        
    def receive(self, *args):
        try:
            self.handler(*args)
        except:
            exception = sys.exc_info()[1]
            Log.error(exception)
        
def connect_safely(event, handler):
    SafeHandler(event, handler)
