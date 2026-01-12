module Einsicht.java.main {
    requires chardet4j;
    requires java.desktop;
    requires javafx.base;
    requires javafx.controls;
    requires javafx.graphics;
    requires org.apache.logging.log4j;
    requires org.eclipse.jdt.annotation;
    requires org.freedesktop.dbus;
    requires org.jspecify;
    requires org.slf4j;
    requires org.objectweb.asm;

    opens de.addiks.einsicht.view to javafx.graphics;
}