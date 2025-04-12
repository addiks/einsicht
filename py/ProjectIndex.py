
import sqlite3

class ProjectIndex:
    def __init__(self, dbFilePath):
        self._dbFilePath = dbFilePath
        self._dbConnection = None
        
    def storeFileContext(self, context):
        for classDef in context.classes():
            for methodDef in classDef.methods():
                print([methodDef])
                
    def search(self, prefix, postfix):
        
        print([prefix, postfix])
        
        connection = self._connection()
        
        return []
        
    def _connection(self):
        if self._dbConnection == None:
            self._dbConnection = sqlite3.connect(self._dbFilePath)
        return self._dbConnection