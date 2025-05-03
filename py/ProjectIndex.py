
from threading import Lock
import sqlite3, os, uuid, hashlib

from py.Languages.LanguageSelector import LanguageSelector
from py.Languages.Language import FileContext

class ProjectIndex:
    def __init__(self, dbFilePath):
        self._dbFilePath = dbFilePath
        self._dbConnection = None
        self._lock = Lock()
        self._inQuery = False
        self._langSelector = None
        
    def storeFileContext(self, context):
        for classDef in context.classes():
            self._storeClassDef(classDef, context)
            
        handle = open(context.filePath, "r")
        fileContents = handle.read()
            
        self._query("""
            INSERT INTO files 
            (filepath, hash, mtime)
            VALUES
            (:filepath, :hash, :mtime)
            ON CONFLICT (filepath) DO
            UPDATE SET hash = :hash, mtime = :mtime
        """, {
            "filepath": context.filePath,
            "hash": hashlib.md5(fileContents.encode()).hexdigest(),
            "mtime": os.stat(context.filePath).st_mtime
        })
        
        self._connection().commit()
                
    def search(self, prefix, postfix):
        
        print([prefix, postfix])
        
        connection = self._connection()
        
        return []
        
    def clear(self):
        self._disconnect()
        if os.path.exists(self._dbFilePath):
            index = 0
            newDbPath = self._dbFilePath
            while os.path.exists(newDbPath):
                newDbPath = self._dbFilePath + "." + str(index) + ".old.db"
                index += 1
            os.rename(self._dbFilePath, newDbPath)
        
    def indexFolder(self, folderPath, rootPath):
        for item in os.listdir(folderPath):
            itemPath = folderPath + "/" + item
    
            if os.path.isfile(itemPath):
                self.indexFile(itemPath, rootPath)
                
            elif os.path.isdir(itemPath):
                self.indexFolder(itemPath, rootPath)

    def indexFile(self, filePath, projectRoot, language=None):
        try:
            if language == None:
                if self._langSelector == None:
                    self._langSelector = LanguageSelector()
                language = self._langSelector.selectForFilePath(filePath)
            
            with open(filePath, "r") as handle:
                fileContents = handle.read()
                
                (syntaxTree, tokens) = language.parse(fileContents)
                
                fileContext = FileContext(
                    filePath, 
                    projectRoot, 
                    syntaxTree,
                    language
                )
                
                language.populateFileContext(fileContext)
                self.storeFileContext(fileContext)
                
        except UnicodeDecodeError:
            pass
    
    def _storeClassDef(self, classDef, context):
        classRows = self._query(
            "SELECT id FROM classes WHERE filepath = :file AND name = :class",
            params={"file": context.filePath, "class": classDef.identifier}
        )
        
        classId = None
        
        if len(classRows) > 0:
            for classRow in classRows:
                classId = classRow[0]
            
        else:
            classId = uuid.uuid4().hex
            self._query("""
                INSERT INTO classes 
                (id, name, namespace, flags, filepath, language, line, column) 
                VALUES 
                (:id, :name, :ns, :flags, :path, :lang, :line, :column)
            """, params={
                "id": classId,
                "name": classDef.identifier,
                "ns": classDef.namespace,
                "flags": ",".join(classDef.flags),
                "path": context.filePath,
                "lang": context.language.name(),
                "line": classDef.node.row,
                "column": classDef.node.col
            })
            
        for methodDef in classDef.methods():
            self._storeMethodDef(methodDef, classId, context)
            
        for memberDef in classDef.members():
            self._storeMemberDef(memberDef, classId, context)
            
    def _storeMethodDef(self, methodDef, classId, context):
        methodRows = self._query(
            "SELECT * FROM classes_methods WHERE class_id = :class AND name = :method",
            params={"method": methodDef.identifier, "class": classId}
        )
        
        methodId = None
        
        if len(methodRows) > 0:
            for methodRow in methodRows:
                methodId = methodRow["id"]
                
        else:
            methodId = uuid.uuid4().hex
            self._query("""
                INSERT INTO classes_methods 
                (id, class_id, name, returntype, flags, line, column) 
                VALUES 
                (:id, :class_id, :name, :returntype, :flags, :line, :column)
            """, params={
                "id": methodId,
                "class_id": classId,
                "name": methodDef.identifier,
                "returntype": methodDef.returntype,
                "flags": ",".join(methodDef.flags),
                "line": methodDef.node.row,
                "column": methodDef.node.col
            })
            
    def _storeMemberDef(self, memberDef, classId, context):
        memberRows = self._query(
            "SELECT * FROM classes_members WHERE class_id = :class AND name = :member",
            params={"member": memberDef.identifier, "class": classId}
        )
        
        memberId = None
        
        if len(memberRows) > 0:
            for memberRow in memberRows:
                memberId = memberRow["id"]
                
        else:
            memberId = uuid.uuid4().hex
            self._query("""
                INSERT INTO classes_members 
                (id, class_id, name, type, flags, line, column) 
                VALUES 
                (:id, :class_id, :name, :type, :flags, :line, :column)
            """, params={
                "id": memberId,
                "class_id": classId,
                "name": memberDef.identifier,
                "type": memberDef.membertype,
                "flags": ",".join(memberDef.flags),
                "line": memberDef.node.row,
                "column": memberDef.node.col
            })
            
    def _classExists(self, identifier, filePath):
        for row in self._query(
            "SELECT 1 FROM classes WHERE filepath = :file AND name = :class",
            params={"file": context.filePath, "class": classDef.identifier}
        ):
            return True
        return False
        
    def _disconnect(self):
        if self._dbConnection != None:
            self._dbConnection.close()
            self._dbConnection = None
        
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
        modifieds = []
        modifieds.append(self._ensureTableSchema("files", [
            {"name": "filepath", "type": "VARCHAR(512)", "pk": 1},
            {"name": "hash", "type": "VARCHAR(32)"},
            {"name": "mtime", "type": "INTEGER"}
        ]))
        modifieds.append(self._ensureTableSchema("classes", [
            {"name": "id", "type": "VARCHAR(32)", "pk": 1},
            {"name": "name", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "namespace", "type": "VARCHAR(512)"},
            {"name": "flags", "type": "VARCHAR(512)"},
            {"name": "filepath", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "language", "type": "VARCHAR(128)", "notnull": 1},
            {"name": "line", "type": "INTEGER"},
            {"name": "column", "type": "SMALLINT"}
        ]))
        modifieds.append(self._ensureTableSchema("classes_methods", [
            {"name": "id", "type": "VARCHAR(32)", "pk": 1},
            {"name": "class_id", "type": "VARCHAR(32)", "notnull": 1},
            {"name": "name", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "returntype", "type": "VARCHAR(512)"},
            {"name": "flags", "type": "VARCHAR(512)"},
            {"name": "arguments", "type": "TEXT"},
            {"name": "line", "type": "INTEGER"},
            {"name": "column", "type": "SMALLINT"}
        ]))
        modifieds.append(self._ensureTableSchema("classes_members", [
            {"name": "id", "type": "VARCHAR(32)", "pk": 1},
            {"name": "class_id", "type": "VARCHAR(32)", "notnull": 1},
            {"name": "name", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "type", "type": "VARCHAR(512)"},
            {"name": "flags", "type": "VARCHAR(512)"},
            {"name": "line", "type": "INTEGER"},
            {"name": "column", "type": "SMALLINT"}
        ]))
        modifieds.append(self._ensureTableSchema("functions", [
            {"name": "id", "type": "VARCHAR(32)", "pk": 1},
            {"name": "name", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "returntype", "type": "VARCHAR(512)"},
            {"name": "flags", "type": "VARCHAR(512)"},
            {"name": "arguments", "type": "TEXT"},
            {"name": "filepath", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "language", "type": "VARCHAR(128)", "notnull": 1},
            {"name": "line", "type": "INTEGER"},
            {"name": "column", "type": "SMALLINT"}
        ]))
        if min(modifieds) == True:
            self._connection().commit()
        
    def _ensureTableSchema(self, tableName, columns):
        schemaModified = False
        if self._tableExists(tableName):
            existingColumns = {}
            for row in self._query("PRAGMA table_info('" + tableName + "')", lock=False):
                existingColumns[row[1]] = row
        
            for column in columns:
                if column["name"] not in existingColumns:
                    columnSql = self._columnToSql(column)
                    self._query(
                        "ALTER TABLE " + tableName + " ADD COLUMN " + columnSql, 
                        lock=False
                    )
                    schemaModified = True
                    
                else:
                    if column["type"] != existingColumns[column["name"]][2]:
                        pass # TODO: modifying columns is not supported in sqlite!
                    del existingColumns[column["name"]]
                    
            for columnName in existingColumns.keys():
                self._query(f"ALTER TABLE {tableName} DROP COLUMN {columnName}", lock=False)
            
        else:
            columnDef = ""
            for column in columns:
                if len(columnDef) > 0:
                    columnDef += ",\n"
                columnDef += "  " + self._columnToSql(column)
            self._query(f"CREATE TABLE {tableName} (\n{columnDef}\n)", lock=False)
            schemaModified = True
        return schemaModified
        
    def _columnToSql(self, column):
        columnDef = column["name"] + " " + column["type"]
        if "pk" in column and int(column["pk"]) == 1:
            columnDef += " NOT NULL PRIMARY KEY"
        elif "notnull" in column and int(column["notnull"]) == 1:
            columnDef += " NOT NULL"
        return columnDef
        
    def _tableExists(self, tableName):
        for row in self._query(
            "SELECT * FROM sqlite_master WHERE type = :type AND name = :name",
            params={"type": "table", "name": tableName},
            lock=False
        ):
            return True
        return False
        
    def _query(self, sql, params={}, lock=True):
        self._inQuery = True
        connection = self._connection()
        self._inQuery = True
        try:
            if lock:
                self._lock.acquire()
            cursor = connection.execute(sql, params)
            return cursor.fetchall()
        finally:
            self._inQuery = False
            if lock:
                self._lock.release()
