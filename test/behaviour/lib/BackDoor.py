from __future__ import annotations

from PySide6 import QtCore, QtWidgets, QtGui, QtDBus
from PySide6.QtCore import Slot, QObject
import os

from py.Hub import Log
from py.Application import Application

class BackDoor(QtCore.QObject):
    def __init__(self, parent: QtCore.QObject, hub: Hub):
        super().__init__(parent)
        self.hub = hub
        self.hub.setup(self)

        self.sessionBus = QtDBus.QDBusConnection.sessionBus()
        self.serviceName = "de.addiks.einsicht.test_" + str(os.getpid())
        
        if not self.sessionBus.isConnected():
            raise Exception(
                "Cannot connect to DBUS: " + self.sessionBus.lastError().message()
            )
         
        self.sessionBus.registerService(self.serviceName)
        self.sessionBus.registerObject(
            '/backdoor', 
            'local.py.einsicht.backdoor', 
            self, 
            QtDBus.QDBusConnection.ExportAllSlots
        )
        
    @Slot()
    def exit(self) -> int:
        Log.debug("Inject call to get(Application).exit()")
        return self.hub.get(Application).exit()
        