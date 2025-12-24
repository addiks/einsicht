package de.addiks.einsicht.filehandling.writing;

import de.addiks.einsicht.filehandling.PartitionedFile;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.nio.file.Path;

public class WriteWholeFileDirectly implements FileWriteStrategy {
    @Override
    public FileWriteStatus writeFile(PartitionedFile file, Path target) throws IOException {
        try (var raf = new RandomAccessFile(target.toFile(), "r")) {
            long length = raf.length();
            CallbackFileWriteStatus.Remote remote = CallbackFileWriteStatus.create(length);
            return remote.status();
        }
    }

}
