package de.addiks.einsicht.filehandling.codings;

import java.nio.charset.Charset;
import java.nio.charset.CharsetDecoder;
import java.util.*;

import static java.lang.System.arraycopy;
import static java.util.Arrays.copyOfRange;

public class DecodedString extends ArrayList<DecodedCharacter> implements MappedString {
    private final Charset charset;
    private final Map<DecodedCharacter, Integer> characterOffsets = new HashMap<>();

    public DecodedString(Charset charset, List<DecodedCharacter> characters) {
        super();
        this.charset = charset;
        int offset = 0;
        for (DecodedCharacter character : characters) {
            characterOffsets.put(character, offset);
            offset += character.bytes().length;
        }
    }

    public DecodedString(Charset charset, byte[] data) {
        this(charset, decode(charset, data));
    }

    public DecodedString substring(int start) {
        return new DecodedString(charset, this.subList(start, size()-1));
    }

    public DecodedString substring(int start, int end) {
        return new DecodedString(charset, this.subList(start, end));
    }

    @Override
    public String asString() {
        StringBuilder stringBuilder = new StringBuilder();
        for (DecodedCharacter character : this) {
            stringBuilder.append(character.character());
        }
        return stringBuilder.toString();
    }

    public Integer offsetOf(DecodedCharacter character) {
        return characterOffsets.getOrDefault(character, null);
    }

    @Override
    public char charAt(int offset) {
        return get(offset).character();
    }

    @Override
    public int length() {
        return size();
    }

    @Override
    public byte[] toByteArray() {
        if (isEmpty()) {
            return new byte[0];
        }
        DecodedCharacter lastChar = getLast();
        int length = offsetOf(lastChar) + lastChar.bytes().length;
        byte[] result = new byte[length];
        for (DecodedCharacter character : this) {
            arraycopy(character.bytes(), 0, result, offsetOf(character), character.bytes().length);
        }
        return result;
    }

    public Builder newBuilder() {
        return new Builder(charset);
    }

    public class Builder implements MappedString.Builder {
        private final Charset charset;
        private final List<DecodedCharacter> characters = new ArrayList<>();

        public Builder(Charset charset) {
            this.charset = charset;
        }

        @Override
        public void append(DecodedCharacter character) {
            characters.add(character);
        }

        @Override
        public MappedString build() {
            return new DecodedString(charset, characters);
        }
    }

    private static List<DecodedCharacter> decode(Charset charset, byte[] data) {
        List<DecodedCharacter> result = new ArrayList<>();
        CharsetDecoder decoder = charset.newDecoder();
        int offset = 0;
        nextIteration:
        while (offset < data.length) {
            for (int length = 1; length <= Math.min(8, data.length - offset); length++) {
                DecodedCharacter character = DecodedCharacter.tryDecode(decoder, copyOfRange(data, offset, offset + length));
                if (character != null && character.valid()) {
                    offset += length;
                    result.add(character);
                    continue nextIteration;
                }
            }
            result.add(new DecodedCharacter(copyOfRange(data, offset, offset + 1), '\0', false));
            offset++;
        }
        return result;
    }
}
