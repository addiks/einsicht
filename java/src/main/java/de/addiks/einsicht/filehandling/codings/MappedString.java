package de.addiks.einsicht.filehandling.codings;

import java.util.List;

public interface MappedString extends List<DecodedCharacter> {
    MappedString substring(int start);
    MappedString substring(int start, int end);
    String asString();
    Integer offsetOf(DecodedCharacter character);
    char charAt(int offset);
    int length();
    byte[] toByteArray();
    Builder newBuilder();

    default int lastIndexOf(String other) {
        int searchLength = length() - other.length();
        int otherLength = other.length();
        char firstChar = other.charAt(0);
        int lastIndex = -1;
        for (int offset = 0; offset < searchLength; offset++) {
            if (firstChar == charAt(offset) && other.equals(substring(offset, offset+otherLength).asString())) {
                lastIndex = offset;
            }
        }
        return lastIndex;
    }

    default int lastIndexOf(MappedString other) {
        int searchLength = length() - other.length();
        int otherLength = other.length();
        char firstChar = other.charAt(0);
        int lastIndex = -1;
        for (int offset = 0; offset < searchLength; offset++) {
            if (firstChar == charAt(offset) && other.equals(substring(offset, offset+otherLength))) {
                lastIndex = offset;
            }
        }
        return lastIndex;
    }

    default boolean contains(String other) {
        int searchLength = length() - other.length();
        int otherLength = other.length();
        char firstChar = other.charAt(0);
        for (int offset = 0; offset < searchLength; offset++) {
            if (firstChar == charAt(offset) && other.equals(substring(offset, offset+otherLength).asString())) {
                return true;
            }
        }
        return false;
    }

    default boolean contains(MappedString other) {
        int searchLength = length() - other.length();
        int otherLength = other.length();
        char firstChar = other.charAt(0);
        for (int offset = 0; offset < searchLength; offset++) {
            if (firstChar == charAt(offset) && other.equals(substring(offset, offset+otherLength))) {
                return true;
            }
        }
        return false;
    }

    default boolean startsWith(MappedString prefix) {
        for (int offset = 0; offset < prefix.length(); offset++) {
            if (prefix.charAt(offset) != charAt(offset)) {
                return false;
            }
        }
        return true;
    }

    default boolean startsWith(String prefix) {
        for (int offset = 0; offset < prefix.length(); offset++) {
            if (prefix.charAt(offset) != charAt(offset)) {
                return false;
            }
        }
        return true;
    }

    default int substringCount(String substring) {
        int count = 0;
        int position = 0;
        while (position < size()) {
            for (int offset = 0; offset < substring.length(); offset++) {
                if (substring.charAt(position + offset) != charAt(position + offset)) {
                    break;
                } else if (offset == substring.length() - 1) {
                    count++;
                }
            }
            position++;
        }
        return count;
    }

    default int substringCount(MappedString substring) {
        int count = 0;
        int position = 0;
        while (position < size()) {
            for (int offset = 0; offset < substring.length(); offset++) {
                if (substring.charAt(position + offset) != charAt(position + offset)) {
                    break;
                } else if (offset == substring.length() - 1) {
                    count++;
                }
            }
            position++;
        }
        return count;
    }

    interface Builder {
        void append(DecodedCharacter character);
        default void append(MappedString string) {
            for (DecodedCharacter character : string) {
                append(character);
            }
        }
        MappedString build();
    }

}
