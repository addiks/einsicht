package de.addiks.einsicht.filehandling.codings;

import org.jspecify.annotations.Nullable;

import java.nio.BufferUnderflowException;
import java.nio.ByteBuffer;
import java.nio.CharBuffer;
import java.nio.charset.CharsetDecoder;
import java.nio.charset.CoderResult;

public record DecodedCharacter(byte[] bytes, char character, boolean valid) {
    public static @Nullable DecodedCharacter tryDecode(CharsetDecoder decoder, byte[] bytes) {
        if (bytes.length < 1) {
            return null;
        }
        decoder.reset();
        ByteBuffer byteBuffer = ByteBuffer.wrap(bytes);
        CharBuffer charBuffer = CharBuffer.allocate(4);
        CoderResult result = decoder.decode(byteBuffer, charBuffer, true);
        decoder.flush(charBuffer);
        charBuffer.rewind();
        try {
            boolean valid = !(result.isError() || result.isMalformed() || result.isUnmappable());
            char character = charBuffer.get();
            return new DecodedCharacter(bytes, character, valid);
        } catch (BufferUnderflowException e) {
            return null;
        }
    }
}
