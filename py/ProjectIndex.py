
import sqlite3, os, uuid, hashlib

from threading import Lock
from PySide6.QtCore import QTimer

from py.Languages.LanguageSelector import LanguageSelector
from py.Languages.Language import FileContext, ClassDef, PositionDef, MethodDef, MemberDef, Language
from py.Hub import Log

class ProjectIndex:
    def __init__(self, dbFilePath: str):
        self._dbFilePath = dbFilePath
        self._dbConnection = None
        self._lock = Lock()
        self._inQuery = False
        self._langSelector = None
        self._classDefs = {}
        self._methodDefs = {}
        self._memberDefs = {}
        self._functionDefs = {}
        self._autoDisconnectDelayCounter = 0
          
    def storeFileContext(self, context: FileContext) -> None:
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
                
    def search(self, prefix: str, postfix: str, node) -> list:
        
        print([prefix, postfix])
        
        connection = self._connection()
        
        return []
        
    def searchClasses(self, prefix: str, postfix: str) -> list[ClassDef]:
    
        connection = self._connection()
        
        classRows = self._query("""
            SELECT 
                id, 
                name, 
                namespace, 
                flags, 
                filepath, 
                language, 
                line, 
                column, 
                offset
            FROM classes 
            WHERE SUBSTR(name, 0, :length) = :prefix
        """, params={"length": len(prefix), "prefix": prefix})
        
        results = []
        
        for row in classRows:
            results.append(ClassDef(
                id=row[0],
                identifier=row[1],
                namespace=row[2],
                flags=row[3],
                position=PositionDef(
                    filepath=row[4],
                    line=row[6],
                    column=row[7],
                    offset=row[8]
                )
            ))
            
        return results
        
    def searchMethods(self, prefix: str, postfix: str) -> list[MethodDef]:
    
        connection = self._connection()
        
        classRows = self._query("""
            SELECT 
                cm.id, 
                cm.name, 
                c.id,
                c.name,
                c.namespace, 
                cm.flags, 
                cm.filepath, 
                c.language, 
                cm.line, 
                cm.column, 
                cm.offset
            FROM classes_methods cm
            LEFT JOIN classes c ON(c.id = cm.class_id)
            WHERE SUBSTR(cm.name, 0, :length) = :prefix
        """, params={"length": len(prefix), "prefix": prefix})
        
        results = []
        
        for row in classRows:
            results.append(ClassDef(
                id=row[0],
                identifier=row[1],
                namespace=row[2],
                flags=row[3],
                position=PositionDef(
                    filepath=row[4],
                    line=row[6],
                    column=row[7],
                    offset=row[8]
                )
            ))
            
        return results
        
    def clear(self) -> None:
        self._disconnect()
        if os.path.exists(self._dbFilePath):
            index = 0
            newDbPath = self._dbFilePath
            while os.path.exists(newDbPath):
                newDbPath = self._dbFilePath + "." + str(index) + ".old.db"
                index += 1
            os.rename(self._dbFilePath, newDbPath)
        
    def indexFolder(self, folderPath: str, rootPath: str) -> None:
        for item in os.listdir(folderPath):
            itemPath = folderPath + "/" + item
    
            if os.path.isfile(itemPath):
                self.indexFile(itemPath, rootPath)
                
            elif os.path.isdir(itemPath):
                self.indexFolder(itemPath, rootPath)

    def indexFile(self, filePath: str, projectRoot: str, language: Language = None) -> None:
        try:
            if language == None:
                if self._langSelector == None:
                    self._langSelector = LanguageSelector()
                language = self._langSelector.selectForFilePath(filePath)
            
            with open(filePath, "r") as handle:
                fileContents = handle.read()
                
                (syntaxTree, tokens) = language.parse(fileContents, filePath)
                
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
    
    def _storeClassDef(self, classDef: ClassDef, context: FileContext) -> None:
        classRows = self._query(
            "SELECT id FROM classes WHERE filepath = :file AND name = :class",
            params={"file": context.filePath, "class": classDef.name}
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
                "name": classDef.name,
                "ns": classDef.namespace,
                "flags": ",".join(classDef.flags),
                "path": context.filePath,
                "lang": context.language.name(),
                "line": classDef.position.row,
                "column": classDef.position.column,
                "offset": classDef.position.offset
            })
            
        for methodDef in classDef.methods():
            self._storeMethodDef(methodDef, classId, context)
            
        for memberDef in classDef.members():
            self._storeMemberDef(memberDef, classId, context)
            
    def _storeMethodDef(self, methodDef: MethodDef, classId: str, context: FileContext) -> None:
        methodRows = self._query(
            "SELECT id FROM classes_methods WHERE class_id = :class AND name = :method",
            params={"method": methodDef.name, "class": classId}
        )
        
        methodId = None
        
        if len(methodRows) > 0:
            for methodRow in methodRows:
                methodId = methodRow[0]
                
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
                "name": methodDef.name,
                "returntype": methodDef.returntype,
                "flags": ",".join(methodDef.flags),
                "line": methodDef.position.row,
                "column": methodDef.position.column,
                "offset": methodDef.position.offset
            })
            
    def _storeMemberDef(self, memberDef: MemberDef, classId: str, context: FileContext) -> None:
        memberRows = self._query(
            "SELECT * FROM classes_members WHERE class_id = :class AND name = :member",
            params={"member": memberDef.name, "class": classId}
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
                "name": memberDef.name,
                "type": memberDef.membertype,
                "flags": ",".join(memberDef.flags),
                "line": memberDef.position.row,
                "column": memberDef.position.column,
                "offset": memberDef.position.offset
            })
            
    def _disconnect(self) -> None:
        if self._dbConnection != None:
            Log.debug("Disconnecting Project Index DB")
            self._dbConnection.close()
            self._dbConnection = None
        
    def _connection(self) -> sqlite3.Connection:
        if self._dbConnection == None:
            try:
                self._lock.acquire()
                if self._dbConnection == None:
                    Log.debug("Connecting Project Index DB")
                    # if not os.path.exists(self._dbFilePath):
                    self._dbConnection = sqlite3.connect(
                        self._dbFilePath,
                        check_same_thread=False
                    )
                    self._checkTables()
            finally:
                self._lock.release()
                
        self._autoDisconnectDelayCounter += 1
        triggeredCounter = self._autoDisconnectDelayCounter
        QTimer.singleShot(5000, lambda: self._checkDelayedAutoDisconnect(triggeredCounter))

        return self._dbConnection
        
    def _checkTables(self) -> None:
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
            {"name": "column", "type": "SMALLINT"},
            {"name": "offset", "type": "INTEGER"}
        ]))
        modifieds.append(self._ensureTableSchema("classes_methods", [
            {"name": "id", "type": "VARCHAR(32)", "pk": 1},
            {"name": "class_id", "type": "VARCHAR(32)", "notnull": 1},
            {"name": "name", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "returntype", "type": "VARCHAR(512)"},
            {"name": "flags", "type": "VARCHAR(512)"},
            {"name": "arguments", "type": "TEXT"},
            {"name": "line", "type": "INTEGER"},
            {"name": "column", "type": "SMALLINT"},
            {"name": "offset", "type": "INTEGER"}
        ]))
        modifieds.append(self._ensureTableSchema("classes_members", [
            {"name": "id", "type": "VARCHAR(32)", "pk": 1},
            {"name": "class_id", "type": "VARCHAR(32)", "notnull": 1},
            {"name": "name", "type": "VARCHAR(512)", "notnull": 1},
            {"name": "type", "type": "VARCHAR(512)"},
            {"name": "flags", "type": "VARCHAR(512)"},
            {"name": "line", "type": "INTEGER"},
            {"name": "column", "type": "SMALLINT"},
            {"name": "offset", "type": "INTEGER"}
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
            {"name": "column", "type": "SMALLINT"},
            {"name": "offset", "type": "INTEGER"}
        ]))
        if min(modifieds) == True:
            self._connection().commit()
        
    def _ensureTableSchema(self, tableName: str, columns: list) -> None:
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
        
    def _columnToSql(self, column: dict) -> str:
        columnDef = column["name"] + " " + column["type"]
        if "pk" in column and int(column["pk"]) == 1:
            columnDef += " NOT NULL PRIMARY KEY"
        elif "notnull" in column and int(column["notnull"]) == 1:
            columnDef += " NOT NULL"
        return columnDef
        
    def _tableExists(self, tableName: str) -> bool:
        for row in self._query(
            "SELECT * FROM sqlite_master WHERE type = :type AND name = :name",
            params={"type": "table", "name": tableName},
            lock=False
        ):
            return True
        return False
        
    def _query(self, sql: str, params: dict = {}, lock: bool = True) -> list:
        self._inQuery = True
        connection = self._connection()
        self._inQuery = True
        try:
            if lock:
                self._lock.acquire()
            # Log.debug(sql)
            cursor = connection.execute(sql, params)
            return cursor.fetchall()
        finally:
            self._inQuery = False
            if lock:
                self._lock.release()
                
    def _checkDelayedAutoDisconnect(self, triggeredCounter: int) -> None:
        if self._autoDisconnectDelayCounter == triggeredCounter:
            self._disconnect()
