package de.addiks.passwordtrainer;

import org.freedesktop.dbus.connections.impl.DBusConnection;
import org.freedesktop.dbus.connections.impl.DBusConnectionBuilder;
import org.freedesktop.dbus.handlers.AbstractPropertiesChangedHandler;
import org.freedesktop.dbus.interfaces.Properties.PropertiesChanged;
import org.freedesktop.dbus.interfaces.DBusSigHandler;
import org.freedesktop.dbus.exceptions.DBusException;
import org.freedesktop.dbus.types.Variant;
import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;
import java.util.function.Consumer;
import java.io.IOException;

public class DBus extends AbstractPropertiesChangedHandler {
    private static final Logger LOGGER = LogManager.getLogger(); 
    
    private final Consumer<Void> onScreenUnlocked;

    public DBus (Consumer<Void> onScreenUnlocked) throws DBusException, IOException
    {
        this.onScreenUnlocked = onScreenUnlocked;
        try (DBusConnection connection = DBusConnectionBuilder.forSessionBus().build()) {
        
        }
    }
    
    public void handle(PropertiesChanged properties) {
    
    }
    
}
