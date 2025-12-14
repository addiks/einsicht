package de.addiks.einsicht.versioning;

import java.nio.file.Path;

public interface Versioning {
    String name();
    Path projectRoot();
    Path metaFolder();
    String status();
    void openUI();
}
