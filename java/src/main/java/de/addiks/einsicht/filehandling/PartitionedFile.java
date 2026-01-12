package de.addiks.einsicht.filehandling;

import com.sigpwned.chardet4j.Chardet;
import de.addiks.einsicht.abstract_syntax_tree.ASTRoot;
import de.addiks.einsicht.filehandling.codings.BinaryString;
import de.addiks.einsicht.filehandling.codings.DecodedString;
import de.addiks.einsicht.filehandling.codings.MappedString;
import de.addiks.einsicht.filehandling.writing.FileWriteStrategy;
import de.addiks.einsicht.filehandling.writing.WriteWholeFileDirectly;
import org.eclipse.jdt.annotation.NonNullByDefault;
import org.jspecify.annotations.NonNull;
import org.jspecify.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.*;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.ReentrantLock;

public class PartitionedFile {
    private static final Logger log = LoggerFactory.getLogger(PartitionedFile.class);
    private final File file;
    private final Partition.Factory partitionFactory;
    private final List<PartitionAtArea> partitions = new ArrayList<>();
    private final Map<Area, PartitionAtArea> areaToPartition = new HashMap<>();
    private final ScheduledExecutorService accessCloser = Executors.newSingleThreadScheduledExecutor();
    private final ReentrantLock lock = new ReentrantLock();

    private @Nullable RandomAccessFile readAccess = null;
    private @Nullable RandomAccessFile writeAccess = null;
    private @Nullable ScheduledFuture<?> accessCloseFuture = null;
    private @Nullable Charset charset = null;
    private boolean wasDetectedAsBinary = false;

    public PartitionedFile(File file, Partition.Factory partitionFactory) {
        this.file = file;
        this.partitionFactory = partitionFactory;
    }

    public boolean isModified() {
        for (PartitionAtArea partitionAtArea : partitions) {
            if (partitionAtArea.partition.modified()) {
                return true;
            }
        }
        return false;
    }

    @NonNullByDefault
    public interface Partition {
        boolean modified();
        MappedString currentContent();
        ASTRoot syntaxTree();
        void resetTo(MappedString content) throws IOException;
        Partition appendBy(Partition other);

        interface Factory {
            Partition create(
                    MappedString dataInPartition,
                    long startingOffset
            ) throws IOException;
            Partition combine(Partition preceedingPartition, Partition followingPartition);
        }
    }

    public List<PartitionAtArea> partitions() {
        return partitions;
    }

    public File file() {
        return file;
    }

    public PartitionAtArea partitionFor(long offset, int length) throws IOException {
        List<PartitionAtArea> foundPartitions = new ArrayList<>();
        List<Area> notCoveredAreas = new ArrayList<>();
        notCoveredAreas.add(new Area(offset, length));

        while (!notCoveredAreas.isEmpty()) {
            Area areaToCover = notCoveredAreas.removeFirst();
            for (PartitionAtArea partitionAtArea : this.partitions) {
                if (partitionAtArea.area.containsWholly(areaToCover)) {
                    foundPartitions.add(partitionAtArea);
                } else if (partitionAtArea.area.overlaps(areaToCover)) {
                    foundPartitions.add(partitionAtArea);
                    notCoveredAreas.addAll(areaToCover.cut(partitionAtArea.area));
                }
            }

            Partition newPartition = partitionFactory.create(readData(areaToCover), areaToCover.offset);

            Area areaBefore = areaDirectlyBefore(areaToCover.offset);
            if (areaBefore != null) {
                PartitionAtArea partitionBefore = areaToPartition.get(areaBefore);
                newPartition = partitionFactory.combine(partitionBefore.partition, newPartition);
                remove(partitionBefore);
            }

            Area areaAfter = areaDirectlyAfter(areaToCover.end());
            if (areaAfter != null) {
                PartitionAtArea partitionAfter = areaToPartition.get(areaAfter);
                newPartition = partitionFactory.combine(newPartition, partitionAfter.partition);
                remove(partitionAfter);
            }

            PartitionAtArea newPartitionAtArea = new PartitionAtArea(newPartition, areaToCover);
            foundPartitions.add(newPartitionAtArea);
            add(newPartitionAtArea);
        }

        if (foundPartitions.size() == 1) {
            return foundPartitions.getFirst();
        }

        foundPartitions.sort((a,b) -> (int) (a.area.offset - b.area.offset));
        PartitionAtArea mergedPartition = foundPartitions.removeFirst();
        remove(mergedPartition);
        while (!foundPartitions.isEmpty()) {
            PartitionAtArea partitionToMerge = foundPartitions.removeFirst();
            remove(partitionToMerge);
            try {
                mergedPartition = mergedPartition.merge(partitionToMerge);
            } catch (Throwable e) {
                add(partitionToMerge);
                throw e;
            } finally {
                add(mergedPartition);
            }
        }

        return mergedPartition;
    }

    public record PartitionAtArea(Partition partition, Area area) {
        public PartitionAtArea merge(PartitionAtArea other) {
            return new PartitionAtArea(
                    partition.appendBy(other.partition),
                    area.extend(other.area)
            );
        }
    }

    public record Area(long offset, int length) {
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
        Area extend(Area other) {
            if (offset == other.offset + other.length) {
                return other.extend(this);
            } else if (offset + length == other.offset) {
                return new Area(offset, length + other.length);
            } else {
                throw new IllegalArgumentException("Can only extend areas that are directly following each other!");
            }
        }
    }

    private void add(PartitionAtArea partitionAtArea) {
        partitions.add(partitionAtArea);
        areaToPartition.put(partitionAtArea.area, partitionAtArea);
    }

    private void remove(PartitionAtArea partitionAtArea) {
        partitions.remove(partitionAtArea);
        areaToPartition.remove(partitionAtArea.area);
    }

    private FileWriteStrategy determineBestWritingStrategy() {
        // TODO
        return new WriteWholeFileDirectly(); // if file is small enough to write all at once
        // return new WritePartitionsShiftEnd(); // if file is too big and NOT enough space for a separate file is free
        // return new WriteToSeparateFile(); // if file is too big and enough space is free
        // Also: Maybe the user should be asked what behaviour is desired?
    }

    private MappedString readData(Area area) throws IOException {
        if (!file.exists()) {
            return new DecodedString(StandardCharsets.UTF_8, List.of());
        }
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
            return byteArrayToString(buffer);
        } finally {
            lock.unlock();
        }
    }

    private void writeData(Area area, MappedString data) throws IOException {
        lock.lock();
        try {
            cancelCurrentFileAccessClosure();
            if (writeAccess == null) {
                writeAccess = new RandomAccessFile(file, "w");
                scheduleFileAccessClosure();
            }
            writeAccess.seek(area.offset);
            writeAccess.write(data.toByteArray());
        } finally {
            lock.unlock();
        }
    }

    private MappedString byteArrayToString(byte[] data) {
        if (charset != null) {
            return new DecodedString(charset, data);
        } else if (wasDetectedAsBinary) {
            return new BinaryString(data);
        } else {
            Optional<Charset> detectedCharset = Chardet.detectCharset(data);
            if (detectedCharset.isPresent()) {
                charset = detectedCharset.get();
                return new DecodedString(charset, data);
            } else {
                wasDetectedAsBinary = true;
                return new BinaryString(data);
            }
        }
    }

    private @Nullable Area areaDirectlyBefore(long offset) {
        for (PartitionAtArea partitionAtArea : partitions) {
            if (partitionAtArea.area.end() == offset - 1) {
                return partitionAtArea.area;
            } else if (partitionAtArea.area.offset > offset) {
                return null;
            }
        }
        return null;
    }

    private @Nullable Area areaDirectlyAfter(long offset) {
        for (PartitionAtArea partitionAtArea : partitions) {
            if (partitionAtArea.area.offset == offset + 1) {
                return partitionAtArea.area;
            } else if (partitionAtArea.area.end() > offset) {
                return null;
            }
        }
        return null;
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

}
