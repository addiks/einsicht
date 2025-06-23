
from py.Log import Log

class SafeHandler:
    def __init__(self, event, handler):
        self.event = event
        self.handler = handler
        
        self.event.connect(self.receive)
        
    def receive(self, event):
        try:
            self.handler(event)
        except:
            exception = sys.exc_info()[1]
            Log.error(exception)
        
def connect_safely(event, handler):
    SafeHandler(event, handler)
    