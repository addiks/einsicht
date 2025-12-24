package de.addiks.einsicht.filehandling.writing;

import de.addiks.einsicht.filehandling.PartitionedFile;
import org.jspecify.annotations.Nullable;

import java.io.File;
import java.io.IOException;
import java.nio.file.Path;

public interface FileWriteStrategy {
    default FileWriteStatus writeFile(PartitionedFile file) throws IOException {
        return writeFile(file, file.file().toPath());
    }

    FileWriteStatus writeFile(PartitionedFile file, Path target) throws IOException;

    interface FileWriteStatus {
        long position();
        long length();
        boolean done();
        boolean failed();
        @Nullable Throwable exception();
    }
}
