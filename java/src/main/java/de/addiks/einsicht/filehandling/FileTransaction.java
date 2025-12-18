package de.addiks.einsicht.filehandling;

import org.apache.logging.log4j.core.util.ExecutorServices;
import org.jspecify.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.locks.ReentrantLock;

public class FileTransaction {
    private static final Logger log = LoggerFactory.getLogger(FileTransaction.class);
    private final File file;
    private final Partition.Factory partitionFactory;
    private final List<DirtyArea> dirtyAreas = new ArrayList<>();
    private final ScheduledExecutorService accessCloser = Executors.newSingleThreadScheduledExecutor();
    private final ReentrantLock lock = new ReentrantLock();

    private @Nullable RandomAccessFile readAccess = null;
    private @Nullable RandomAccessFile writeAccess = null;
    private @Nullable ScheduledFuture<?> accessCloseFuture = null;

    public FileTransaction(File file, Partition.Factory partitionFactory) {
        this.file = file;
        this.partitionFactory = partitionFactory;
    }

    public interface Partition {
        boolean modified();
        byte[] currentContent();
        void resetTo(byte[] content);

        interface Factory {
            Partition create(
                    byte[] originalContent,
                    @Nullable Partition preceedingPartition,
                    @Nullable Partition followingPartition
            );
        }
    }

    public List<Partition> partitionsFor(long offset, int length) throws IOException {
        List<Partition> partitions = new ArrayList<>();
        List<Area> notCoveredAreas = new ArrayList<>();
        notCoveredAreas.add(new Area(offset, length));

        while (!notCoveredAreas.isEmpty()) {
            Area areaToCover = notCoveredAreas.removeFirst();

            for (DirtyArea dirtyArea : dirtyAreas) {
                if (dirtyArea.area.containsWholly(areaToCover)) {
                    partitions.add(dirtyArea.partition);

                } else if (dirtyArea.area.overlaps(areaToCover)) {
                    partitions.add(dirtyArea.partition);
                    notCoveredAreas.addAll(areaToCover.cut(dirtyArea.area));
                }
            }

            Partition newPartition = partitionFactory.create(
                    readData(areaToCover),
                    partitionDirectlyBefore(areaToCover.offset),
                    partitionDirectlyAfter(areaToCover.end())
            );
            partitions.add(newPartition);
            dirtyAreas.add(new DirtyArea(newPartition, areaToCover));
        }

        return partitions;
    }

    public void commit() throws IOException {
        for (DirtyArea dirtyArea : dirtyAreas) {
            if (dirtyArea.partition.modified()) {
                writeData(dirtyArea.area, dirtyArea.partition.currentContent());
            }
        }
    }

    public void rollback() throws IOException {
        for (DirtyArea dirtyArea : dirtyAreas) {
            if (dirtyArea.partition.modified()) {
                dirtyArea.partition.resetTo(readData(dirtyArea.area));
            }
        }
    }

    private byte[] readData(Area area) throws IOException {
        lock.lock();
        try {
            cancelCurrentFileAccessClosure();
            if (readAccess == null) {
                readAccess = new RandomAccessFile(file, "r");
                scheduleFileAccessClosure();
            }
            readAccess.seek(area.offset);
            byte[] buffer = new byte[area.length];
            readAccess.read(buffer, 0, area.length);
            return buffer;
        } finally {
            lock.unlock();
        }
    }

    private void writeData(Area area, byte[] data) throws IOException {
        lock.lock();
        try {
            cancelCurrentFileAccessClosure();
            if (writeAccess == null) {
                writeAccess = new RandomAccessFile(file, "w");
                scheduleFileAccessClosure();
            }
            writeAccess.seek(area.offset);
            writeAccess.write(data);
        } finally {
            lock.unlock();
        }
    }

    private @Nullable Partition partitionDirectlyBefore(long offset) {

    }

    private @Nullable Partition partitionDirectlyAfter(long offset) {

    }

    private void cancelCurrentFileAccessClosure() {
        if (accessCloseFuture != null) {
            accessCloseFuture.cancel(true);
        }
    }

    private void scheduleFileAccessClosure() {
        accessCloseFuture = accessCloser.schedule(this::closeFileAccess, 50, TimeUnit.MILLISECONDS);
    }

    private void closeFileAccess() {
        try {
            if (readAccess != null) {
                readAccess.close();
            }
            if (writeAccess != null) {
                writeAccess.close();
            }
        } catch (IOException e) {
            log.error("Exception white closing file access: {}", e.getMessage(), e);
        } finally {
            accessCloseFuture = null;
        }
    }

    private record DirtyArea(Partition partition, Area area) {}
    private record Area(long offset, int length) {
        long end() {
            return offset + length;
        }
        boolean containsWholly(Area other) {
            return offset <= other.offset && end() >= other.end();
        }
        boolean overlapsAtBeginning(Area other) {
            return offset <= other.offset && end() <= other.end();
        }
        boolean overlaps(Area other) {
            return overlapsAtBeginning(other) || overlapsAtEnd(other);
        }
        boolean overlapsAtEnd(Area other) {
            return offset >= other.offset && end() >= other.end();
        }
        List<Area> cut(Area cutout) {
            if (cutout.containsWholly(this)) {
                return List.of();
            }
            if (!overlaps(cutout)) {
                return List.of(this);
            }
            List<Area> cutOuts = new ArrayList<>();
            if (offset < cutout.offset) {
                cutOuts.add(new Area(offset, (int) (cutout.offset - offset)));
            }
            if (end() > cutout.end()) {
                cutOuts.add(new Area(end(), (int) (end() - cutout.end())));
            }
            return cutOuts;
        }
    }

}
