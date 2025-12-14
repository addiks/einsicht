package de.addiks.einsicht;

import org.freedesktop.dbus.connections.impl.DBusConnection;
import org.freedesktop.dbus.connections.impl.DBusConnectionBuilder;
import org.freedesktop.dbus.exceptions.DBusException;

public class MessageBroker {
    private final Hub hub;
    private final String serviceName;
    private final DBusConnection sessionBus;

    public MessageBroker(Hub hub) throws Exception {
        this.hub = hub;
        String filePath = hub.get(FileAccess.class).filePath();
        serviceName = "de.addiks.einsicht.file_" + Application.md5(filePath);
        sessionBus = DBusConnectionBuilder.forSessionBus().build();

        if (!sessionBus.isConnected()) {
            throw new Exception("Cannot connect to DBUS: " + sessionBus.getError().getMessage(), sessionBus.getError());
        }

    }

    public void close() {

    }

    public void presentSelf() {

    }

    public class FileAlreadyOpenOnOtherProcessException extends Exception {}
}
