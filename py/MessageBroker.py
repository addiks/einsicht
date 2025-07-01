from __future__ import annotations

from PySide6 import QtCore, QtWidgets, QtGui, QtDBus
from PySide6.QtCore import Slot, QObject
import hashlib
from typing import Annotated, get_type_hints

from py.Api import FileAccess

class FileAlreadyOpenOnOtherProcessException(Exception): 
    pass

class MessageBroker(QtCore.QObject):
    def __init__(self, parent: QtCore.QObject, hub: Hub):
        super().__init__(parent)
        self.hub = hub
        
        filePath = self.hub.get(FileAccess).filePath()	
        
        self.serviceName = "de.addiks.einsicht.file_" + hashlib.md5(
            filePath.encode('UTF-8')
        ).hexdigest()
        
        self.sessionBus = QtDBus.QDBusConnection.sessionBus()
        
        if not self.sessionBus.isConnected():
            raise Exception(
                "Cannot connect to DBUS: " + self.sessionBus.lastError().message()
            )
         
        if not self.sessionBus.registerService(self.serviceName):
            interface = QtDBus.QDBusInterface(self.serviceName, '/file', '', self.sessionBus)
            interface.call('presentSelf')
            raise FileAlreadyOpenOnOtherProcessException()
        
        self.sessionBus.registerObject(
            '/file', 
            'local.py.einsicht.file', 
            self, 
            QtDBus.QDBusConnection.ExportAllSlots
        )
        
    @Slot(str, result=str)
    def test(self, arg: str) -> str:
        return "foo " + arg
        
    @Slot()
    def presentSelf(self) -> None:
        self.hub.notify(self.presentSelf)
        
