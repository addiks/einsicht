package de.addiks.einsicht.filehandling.writing;

import org.jspecify.annotations.Nullable;

import java.util.function.Consumer;

public class CallbackFileWriteStatus implements FileWriteStrategy.FileWriteStatus {
    private final long length;

    private long position = 0;
    private @Nullable Throwable exception;

    private CallbackFileWriteStatus(long length) {
        this.length = length;
    }

    public static Remote create(long length) {
        CallbackFileWriteStatus status = new CallbackFileWriteStatus(length);
        return new Remote(
                status,
                (Long p) -> status.position = p,
                (Throwable t) -> status.exception = t
        );
    }

    public record Remote(
            CallbackFileWriteStatus status,
            Consumer<Long> setPosition,
            Consumer<Throwable> errorHappened
    ) {}

    @Override
    public long position() {
        return position;
    }

    @Override
    public long length() {
        return length;
    }

    @Override
    public boolean done() {
        return position >= length;
    }

    @Override
    public boolean failed() {
        return exception != null;
    }

    @Override
    public @Nullable Throwable exception() {
        return exception;
    }
}
