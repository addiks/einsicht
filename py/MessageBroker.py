from __future__ import annotations

from PySide6 import QtCore, QtWidgets, QtGui, QtDBus
from PySide6.QtCore import Slot, QObject
import hashlib
from typing import Annotated, get_type_hints

class FileAlreadyOpenOnOtherProcessException(Exception):
    pass

class MessageBroker(QtCore.QObject):
    
    def __init__(self, editorWindow):
        super().__init__(editorWindow)
        
        filePath = editorWindow.filePath		
        
        self.serviceName = "de.addiks.qtedit.file_" + hashlib.md5(filePath.encode('UTF-8')).hexdigest()
        self.editorWindow = editorWindow
        
        self.sessionBus = QtDBus.QDBusConnection.sessionBus()
        
        if not self.sessionBus.isConnected():
            raise Exception("Cannot connect to DBUS: " + self.sessionBus.lastError().message())
         
        if not self.sessionBus.registerService(self.serviceName):
            interface = QtDBus.QDBusInterface(self.serviceName, '/file', '', self.sessionBus)
            interface.call('presentSelf')
            raise FileAlreadyOpenOnOtherProcessException()
        
        self.sessionBus.registerObject('/file', 'local.py.qtedit.file', self, QtDBus.QDBusConnection.ExportAllSlots)
        
    @Slot(str, result=str)
    def test(self, arg):
        return "foo " + arg
        
    @Slot()
    def presentSelf(self):
        self.editorWindow.presentSelf()
        pass
        
