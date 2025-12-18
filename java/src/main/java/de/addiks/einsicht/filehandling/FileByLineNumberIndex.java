package de.addiks.einsicht.filehandling;

import org.jspecify.annotations.Nullable;

import java.io.*;
import java.util.ArrayList;
import java.util.List;

/**
 * An in-memory index to quickly find the position for a line-number in a huge file.
 * (Tested against up to ~10 gigabyte long ASCII files, indexing these should be less than 20 seconds)
 */
public class FileByLineNumberIndex {
    private static final int BUFFER_SIZE = 4096;
    private final File file;
    private final List<Milestone> milestones = new ArrayList<>();
    private final int lastLine;
    private final long lastOffset;
    private final int milestoneSize;

    private record Milestone(int line, long offset) {}

    private @Nullable FileByLineNumberIndex lastUsedInnerIndex;

    public FileByLineNumberIndex(File file) throws IOException {
        this(file, 1024);
    }

    public FileByLineNumberIndex(
            File file,
            int milestoneSize
    ) throws IOException {
        this(file, milestoneSize, 1, null, null);
    }

    public FileByLineNumberIndex(
            File file,
            int milestoneSize,
            int firstLineNumber,
            @Nullable Long begin,
            @Nullable Long end
    ) throws IOException {
        this.file = file;
        this.milestoneSize = milestoneSize;
        try (RandomAccessFile handle = new RandomAccessFile(file, "r")) {
            if (begin != null) {
                handle.seek(begin);
            } else {
                begin = 0L;
            }
            if (end == null) {
                end = begin + handle.length();
            }
            long milestoneDistance = (end - begin) / milestoneSize;
            byte[] buffer = new byte[BUFFER_SIZE];
            long offset = begin;
            long lastMilestone = begin;
            int lineNumber = firstLineNumber;
            milestones.add(new Milestone(lineNumber, lastMilestone));
            while (handle.getFilePointer() < end) {
                int bytesRead = handle.read(buffer, 0, BUFFER_SIZE);
                for (int i = 0; i < bytesRead; i++) {
                    // 10 = line feed
                    if (10 == (int) buffer[i]) {
                        lineNumber++;
                        if ((offset + i) - lastMilestone > milestoneDistance) {
                            lastMilestone = (offset + i);
                            milestones.add(new Milestone(lineNumber, lastMilestone));
                        }
                    }
                }
                offset += bytesRead;
            }
            lastLine = lineNumber;
            lastOffset = end;
        }
    }

    public long offsetAtLine(int line) throws IOException {
        if (lastUsedInnerIndex != null && lastUsedInnerIndex.containsLine(line)) {
            return lastUsedInnerIndex.offsetAtLine(line);
        }
        Milestone previousMilestone = milestones.getFirst();
        for (Milestone milestone : milestones) {
            if (milestone == previousMilestone) {
                continue;
            }
            if (milestone.line == line) {
                return milestone.offset;
            } else if (milestone.line > line) {
                if (milestone.line - line < 100) {
                    return searchOffsetLinearlyIn(
                            file,
                            previousMilestone.offset,
                            milestone.offset,
                            previousMilestone.line,
                            line
                    );
                } else {
                    lastUsedInnerIndex = new FileByLineNumberIndex(
                            file,
                            milestoneSize,
                            previousMilestone.line,
                            previousMilestone.offset,
                            milestone.offset
                    );
                    return lastUsedInnerIndex.offsetAtLine(line);
                }
            }
            previousMilestone = milestone;
        }
        return lastOffset;
    }

    public int lineAtOffset(long offset) throws IOException {
        if (lastUsedInnerIndex != null && lastUsedInnerIndex.containsOffset(offset)) {
            return lastUsedInnerIndex.lineAtOffset(offset);
        }
        Milestone previousMilestone = milestones.getFirst();
        for (Milestone milestone : milestones) {
            if (milestone == previousMilestone) {
                continue;
            }
            if (milestone.offset == offset) {
                return milestone.line;
            } else if (milestone.offset > offset) {
                if (milestone.offset - offset < BUFFER_SIZE) {
                    return searchLineNumberLinearlyIn(
                            file,
                            previousMilestone.offset,
                            milestone.offset,
                            previousMilestone.line,
                            offset
                    );
                } else {
                    lastUsedInnerIndex = new FileByLineNumberIndex(
                            file,
                            milestoneSize,
                            previousMilestone.line,
                            previousMilestone.offset,
                            milestone.offset
                    );
                    return lastUsedInnerIndex.lineAtOffset(offset);
                }
            }
            previousMilestone = milestone;
        }
        return lastLine;
    }

    private boolean containsOffset(long offset) {
        return offset >= firstOffset() && offset <= lastOffset();
    }

    private long firstOffset() {
        return milestones.getFirst().offset;
    }

    private long lastOffset() {
        return lastOffset;
    }

    public boolean containsLine(int line) {
        return line >= firstLine() && line <= lastLine();
    }

    public int firstLine() {
        return milestones.getFirst().line;
    }

    public int lastLine() {
        return lastLine;
    }

    private static long searchOffsetLinearlyIn(
            File file,
            long beginOffset,
            long endOffset,
            int firstLineNumber,
            int targetLine
    ) throws IOException {
        try (RandomAccessFile handle = new RandomAccessFile(file, "r")) {
            int lineNumber = firstLineNumber;
            byte[] buffer = new byte[BUFFER_SIZE];
            long offset = beginOffset;
            while (handle.getFilePointer() < endOffset) {
                int bytesRead = handle.read(buffer, 0, BUFFER_SIZE);
                for (int i = 0; i < bytesRead; i++) {
                    // 10 = line feed
                    if (10 == (int) buffer[i]) {
                        lineNumber++;
                    }
                    if (lineNumber == targetLine) {
                        return offset+i;
                    }
                }
                offset += bytesRead;
            }
            return offset;
        }
    }

    private static int searchLineNumberLinearlyIn(
            File file,
            long beginOffset,
            long endOffset,
            int firstLineNumber,
            long targetOffset
    ) throws IOException {
        try (RandomAccessFile handle = new RandomAccessFile(file, "r")) {
            int lineNumber = firstLineNumber;
            byte[] buffer = new byte[BUFFER_SIZE];
            long offset = beginOffset;
            while (handle.getFilePointer() < endOffset) {
                int bytesRead = handle.read(buffer, 0, BUFFER_SIZE);
                for (int i = 0; i < bytesRead; i++) {
                    // 10 = line feed
                    if (10 == (int) buffer[i]) {
                        lineNumber++;
                    }
                    if ((offset+i) == targetOffset) {
                        return lineNumber;
                    }
                }
                offset += bytesRead;
            }
            return lineNumber;
        }
    }

    static public void main(String[] argv) throws IOException, InterruptedException {

        File file = new File("/home/gerrit/test/some-big-logfile.log");

        FileByLineNumberIndex index = new FileByLineNumberIndex(file, 1024);

        System.out.println("line: " + index.lineAtOffset(103));
    }
}
