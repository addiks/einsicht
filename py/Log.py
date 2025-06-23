
import traceback

class Log:
    _logger = None
    _prefix = ""

    @staticmethod
    def registerLogger(logger):
        Log._logger = logger

    @staticmethod
    def setPrefix(prefix):
        Log._prefix = prefix

    @staticmethod
    def debug(message):
        message = Log._prepareMessage(message)
        if Log._logger != None:
            Log._logger.debug(message)
        else:
            print(message)
        
    @staticmethod
    def info(message):
        message = Log._prepareMessage(message)
        if Log._logger != None:
            Log._logger.info(message)
        else:
            print(message)
        
    @staticmethod
    def error(message):
        message = Log._prepareMessage(message)
        if Log._logger != None:
            Log._logger.error(message)
        print(message)
        
    @staticmethod
    def normalize(target):
        if isinstance(target, Exception):
            target = "".join(traceback.format_exception(target))
    
        return target
        
    def _prepareMessage(message):
        message = Log.normalize(message)
        return Log._prefix + str(message)