
from threading import Lock
import sqlite3, os, uuid, hashlib

class ProjectIndex:
    def __init__(self, dbFilePath):
        self._dbFilePath = dbFilePath
        self._dbConnection = None
        self._lock = Lock()
        
    def storeFileContext(self, context):
        print("*storeFileContext*")
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
        
    def _storeClassDef(self, classDef, context):
        for methodDef in classDef.methods():
            print([methodDef])
        
        classRows = self._query(
            "SELECT * FROM classes WHERE filepath = :file AND name = :class",
            params={"file": context.filePath, "class": classDef.identifier}
        )
        
        if len(classRows) > 0:
            for classRow in classRows:
                pass
            
        else:
            self._query("""
                INSERT INTO classes 
                (id, name, namespace, flags, filepath, language, line, column) 
                VALUES 
                (:id, :name, :ns, :flags, :path, :lang, :line, :column)
            """, params={
                "id": uuid.uuid4().hex,
                "name": classDef.identifier,
                "ns": classDef.namespace,
                "flags": ",".join(classDef.flags),
                "path": context.filePath,
                "lang": context.language.name(),
                "line": classDef.node.row,
                "column": classDef.node.col
            })
            
    def _classExists(self, identifier, filePath):
        for row in self._query(
            "SELECT 1 FROM classes WHERE filepath = :file AND name = :class",
            params={"file": context.filePath, "class": classDef.identifier}
        ):
            return True
        return False
        
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
        modified = False
        modified = modified or self._ensureTableSchema("files", [
            {"name": "filepath", "type": "VARCHAR(512)", "pk": 1},
            {"name": "hash", "type": "VARCHAR(32)"},
            {"name": "mtime", "type": "INTEGER"}
        ])
        modified = modified or self._ensureTableSchema("classes", [
            {"name": "id", "type": "VARCHAR(32)", "pk": 1},
            {"name": "name", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "namespace", "type": "VARCHAR(512)"},
            {"name": "flags", "type": "VARCHAR(512)"},
            {"name": "filepath", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "language", "type": "VARCHAR(128)", "notnull": 1},
            {"name": "line", "type": "INTEGER"},
            {"name": "column", "type": "SMALLINT"}
        ])
        modified = modified or self._ensureTableSchema("classes_methods", [
            {"name": "id", "type": "VARCHAR(32)", "pk": 1},
            {"name": "class_id", "type": "VARCHAR(32)", "notnull": 1},
            {"name": "name", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "returntype", "type": "VARCHAR(512)"},
            {"name": "flags", "type": "VARCHAR(512)"},
            {"name": "arguments", "type": "TEXT"},
            {"name": "filepath", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "line", "type": "INTEGER"},
            {"name": "column", "type": "SMALLINT"}
        ])
        modified = modified or self._ensureTableSchema("classes_members", [
            {"name": "id", "type": "VARCHAR(32)", "pk": 1},
            {"name": "class_id", "type": "VARCHAR(32)", "notnull": 1},
            {"name": "name", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "type", "type": "VARCHAR(512)"},
            {"name": "flags", "type": "VARCHAR(512)"},
            {"name": "filepath", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "line", "type": "INTEGER"},
            {"name": "column", "type": "SMALLINT"}
        ])
        modified = modified or self._ensureTableSchema("functions", [
            {"name": "id", "type": "VARCHAR(32)", "pk": 1},
            {"name": "name", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "returntype", "type": "VARCHAR(512)"},
            {"name": "flags", "type": "VARCHAR(512)"},
            {"name": "arguments", "type": "TEXT"},
            {"name": "filepath", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "language", "type": "VARCHAR(128)", "notnull": 1},
            {"name": "line", "type": "INTEGER"},
            {"name": "column", "type": "SMALLINT"}
        ])
        if modified:
            print("*commit*")
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
                    
                elif column["type"] != existingColumns[column["name"]][2]:
                    pass # TODO: modifying columns is not supported in sqlite!
            
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
        connection = self._connection()
        try:
            if lock:
                self._lock.acquire()
            print([sql, params])
            cursor = connection.execute(sql, params)
            return cursor.fetchall()
        finally:
            if lock:
                self._lock.release()