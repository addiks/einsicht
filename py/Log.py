
import traceback

from logging import Logger
from typing import Any


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