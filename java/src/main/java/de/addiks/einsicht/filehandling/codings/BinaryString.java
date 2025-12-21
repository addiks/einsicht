package de.addiks.einsicht.filehandling.codings;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import static java.lang.System.arraycopy;

public class BinaryString extends ArrayList<DecodedCharacter> implements MappedString {
    private final byte[] data;
    private final Map<DecodedCharacter, Integer> characterOffsets = new HashMap<>();

    public BinaryString(byte[] data) {
        this.data = data;
        int offset = 0;
        for (byte b : data) {
            DecodedCharacter character = new DecodedCharacter(new byte[]{b}, (char)b, true);
            add(character);
            characterOffsets.put(character, offset);
            offset++;
        }
    }

    public BinaryString(List<DecodedCharacter> characters) {
        this(collectBytes(characters));
    }

    @Override
    public BinaryString substring(int start) {
        return new BinaryString(this.subList(start, size()-1));
    }

    @Override
    public BinaryString substring(int start, int end) {
        return new BinaryString(this.subList(start, end));
    }

    @Override
    public String asString() {
        StringBuilder stringBuilder = new StringBuilder();
        for (byte datum : data) {
            stringBuilder.append((char) datum);
        }
        return stringBuilder.toString();
    }

    @Override
    public Integer offsetOf(DecodedCharacter character) {
        return characterOffsets.getOrDefault(character, null);
    }

    @Override
    public char charAt(int offset) {
        return (char) data[offset];
    }

    @Override
    public int length() {
        return data.length;
    }

    @Override
    public byte[] toByteArray() {
        return data;
    }

    public BinaryString.Builder newBuilder() {
        return new BinaryString.Builder();
    }

    public class Builder implements MappedString.Builder {
        private final List<DecodedCharacter> characters = new ArrayList<>();

        @Override
        public void append(DecodedCharacter character) {
            characters.add(character);
        }

        @Override
        public MappedString build() {
            return new BinaryString(characters);
        }
    }

    private static byte[] collectBytes(List<DecodedCharacter> characters) {
        int length = 0;
        for (DecodedCharacter character : characters) {
            length += character.bytes().length;
        }
        byte[] data = new byte[length];
        int offset = 0;
        for (DecodedCharacter character : characters) {
            arraycopy(character.bytes(), 0, data, offset, character.bytes().length);
            offset += character.bytes().length;
        }
        return data;
    }
}
