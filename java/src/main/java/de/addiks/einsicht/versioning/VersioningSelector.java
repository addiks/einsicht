package de.addiks.einsicht.versioning;

import de.addiks.einsicht.Hub;
import org.jspecify.annotations.Nullable;

import java.nio.file.Path;

public class VersioningSelector {
    private final Hub hub;
    public VersioningSelector (Hub hub) {
        this.hub = hub;
    }

    public @Nullable Versioning selectVersioningFor(Path filePath) {
        Versioning versioning = null;

        return versioning;
    }
    
}
