
from threading import Lock
import sqlite3, os

class ProjectIndex:
    def __init__(self, dbFilePath):
        self._dbFilePath = dbFilePath
        self._dbConnection = None
        self._lock = Lock()
        
    def storeFileContext(self, context):
        print("*storeFileContext*")
        for classDef in context.classes():
            self._storeClassDef(classDef, context)
                
    def search(self, prefix, postfix):
        
        print([prefix, postfix])
        
        connection = self._connection()
        
        return []
        
    def _storeClassDef(self, classDef, context):
        for methodDef in classDef.methods():
            print([methodDef])
        
    def _connection(self):
        if self._dbConnection == None:
            try:
                self._lock.acquire()
                if self._dbConnection == None:
                    # if not os.path.exists(self._dbFilePath):
                    self._dbConnection = sqlite3.connect(
                        self._dbFilePath,
                        check_same_thread=False
                    )
                    self._checkTables()
            finally:
                self._lock.release()
        return self._dbConnection
        
    def _checkTables(self):
        pass
        
    def _query(self, sql):
        pass