package de.addiks.einsicht.filehandling.codings;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

import static org.junit.jupiter.api.Assertions.*;

public class DecodedStringTest {

    @ParameterizedTest
    @MethodSource("dataProviderForShouldDecodeBytesPerChar")
    public void shouldDecodeBytesPerChar(String charsetName, byte[] bytes, int invalidOffset) {
        Charset charset = Charset.forName(charsetName);

        DecodedString decodedString = new DecodedString(charset, bytes);

        for (int offset = 0; offset < decodedString.size(); offset++) {
            DecodedCharacter character = decodedString.get(offset);
            // System.out.println("Offset %d: %s character%s represented by %d bytes".formatted(
            //         offset,
            //         character.valid() ? "Valid" : "Invalid",
            //         character.valid() ? " " + character.character() : "",
            //         character.bytes().length
            // ));
            assertEquals(offset != invalidOffset, character.valid(), "Error at offset " + offset);
        }

    }

    public static Stream<Arguments> dataProviderForShouldDecodeBytesPerChar() {
        List<Arguments> calls = new ArrayList<>();

        calls.add(Arguments.of("UTF8", new byte[] {
                0x41,                                               // 'A' (1 Byte)
                (byte) 0xC3, (byte) 0xA4,                           // 'ä' (2 Bytes)
                (byte) 0xE2, (byte) 0x82, (byte) 0xAC,              // '€' (3 Bytes)
                (byte) 0xF0, (byte) 0x9F, (byte) 0x98, (byte) 0x80, // 😀 (4 Bytes)
                (byte) 0xCC, (byte) 0x81,                           // ◌́  combining acute accent
                (byte) 0xC3,                                        // INVALID (truncated UTF-8)
        }, 5));

        calls.add(Arguments.of("UTF_16LE", new byte[] {
                0x41, 0x00,                           // 'A'
                (byte) 0xE4, 0x00,                    // 'ä'
                (byte) 0xAC, 0x20,                    // '€'
                0x3D, (byte) 0xD8, 0x00, (byte) 0xDE, // 😀 (surrogate pair)
                0x00                                  // INVALID: odd byte count
        }, 4));

        calls.add(Arguments.of("ISO-8859-1", new byte[] {
                0x41,        // 'A'
                (byte) 0xE4, // 'ä'
                (byte) 0xDF, // 'ß'
                (byte) 0xFF  // 'ÿ'
        }, -1));

        calls.add(Arguments.of("CP1252", new byte[] {
                0x41,        // 'A'
                (byte) 0x80, // '€'
                (byte) 0x91, // ‘
                (byte) 0x92, // ’
                (byte) 0x96  // –
        }, -1));

        calls.add(Arguments.of("SHIFT_JIS:2004", new byte[] {
                0x41,                     // 'A'
                (byte) 0x82, (byte) 0xA0, // あ
                (byte) 0x82, (byte) 0xA2, // い
                (byte) 0x82               // INVALID (lead byte ohne trail)
        }, 3));

        calls.add(Arguments.of("EUC_JP", new byte[] {
                0x41,                     // A
                (byte) 0xA4, (byte) 0xA2, // あ
                (byte) 0xC8, (byte) 0xBE, // 半
                (byte) 0xB3, (byte) 0xD1, // 角
                (byte) 0xA5, (byte) 0xCA  // ナ
        }, -2));

        calls.add(Arguments.of("ASCII", new byte[] {
                0x41,        // 'A'
                0x42,        // 'B'
                (byte) 0x80, // INVALID
                0x43         // 'C'
        }, 2));

        return calls.stream();
    }

    @Test
    public void shouldRecognizeInvalidByteArray() {



    }

    private static byte[] MIXED_STRESS_TEST = new byte[] {
        0x41,
        (byte) 0xC3, (byte) 0xA4,
        (byte) 0xF0, (byte) 0x9F, (byte) 0x98, (byte) 0x80,
        (byte) 0xED, (byte) 0xA0, (byte) 0x80, // UTF-8 surrogate half (illegal)
        (byte) 0x80,
        0x42
    };

}
