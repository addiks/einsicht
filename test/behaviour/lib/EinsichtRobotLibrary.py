
import sys, os, logging, threading, time, subprocess
from os.path import dirname, abspath
from robot.api import logger

sys.path.append(dirname(dirname(dirname(dirname(abspath(__file__))))))

from robot.api.logger import info, debug, trace, console

from PySide6.QtCore import QEventLoop, QCoreApplication
from PySide6 import QtWidgets, QtGui, QtDBus

from py.Hub import Hub, Log
from py.Application import Application

# https://robotframework.org/?tab=0#getting-started

class EinsichtRobotLibrary:

    ROBOT_LIBRARY_SCOPE = 'SUITE'

    def __init__(self) -> None:
        self.interface = None
        self.serviceName = None
        self.sessionBus = QtDBus.QDBusConnection.sessionBus()
        if not self.sessionBus.isConnected():
            raise Exception(
                "Cannot connect to DBUS: " + self.sessionBus.lastError().message()
            )
        
    def create_a_new_file(self):
        self._start1SProcess([])
        self.interface = self._connectToBackdoor()
        
    def close_the_file(self):
        self.interface.call('exit')
        self._subprocess.terminate()
        
    def _start1SProcess(self, args: list) -> subprocess.Popen:
        testBaseDir = dirname(dirname(abspath(__file__)))
        baseDir = dirname(dirname(testBaseDir))
        self._subprocess = subprocess.Popen([baseDir + "/env/bin/python3", testBaseDir + "/bin/1s.backdoored.py"] + args)
        time.sleep(0.5)
        
    def _connectToBackdoor(self) -> QtDBus.QDBusInterface:
        self._serviceName = "de.addiks.einsicht.test_" + str(self._subprocess.pid)
        interface = QtDBus.QDBusInterface(self._serviceName, '/backdoor', '', self.sessionBus)
        if interface.lastError().isValid():
            raise Exception("QDbus: " + interface.lastError().message())
        return interface
        